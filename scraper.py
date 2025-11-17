# -*- coding: utf-8 -*-
import sys
import io

# Windows コンソールでUTF-8を使用
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# ==========================
# 🎯 カテゴリに応じた検索キーワード最適化
# ==========================
def optimize_search_query(product_name, category):
    """カテゴリに応じて検索クエリを最適化"""
    # 日本語キーワードを追加すると価格.comで404エラーになるため
    # 商品名のみを返す
    return product_name


# ==========================
# 📊 スペック情報の抽出
# ==========================
def extract_cpu_specs(product_name):
    """CPUの商品名からソケット情報を抽出"""
    specs = {}
    import re

    # ソケット情報のパターン
    socket_patterns = {
        'LGA1700': ['LGA1700', 'LGA 1700'],
        'LGA1200': ['LGA1200', 'LGA 1200'],
        'LGA1151': ['LGA1151', 'LGA 1151'],
        'AM5': ['AM5', 'Socket AM5'],
        'AM4': ['AM4', 'Socket AM4'],
        'sTRX4': ['sTRX4', 'TRX4'],
        'sTR4': ['sTR4', 'TR4'],
    }

    # CPUモデルからソケットを推定
    product_lower = product_name.lower()

    # TDP情報を抽出
    tdp_patterns = [
        r'tdp\s*(\d{2,3})\s*w',
        r'(\d{2,3})\s*w\s*tdp',
    ]
    for pattern in tdp_patterns:
        match = re.search(pattern, product_lower)
        if match:
            specs['tdp'] = match.group(1) + 'W'
            print(f"  ⚡ 検出したTDP: {specs['tdp']}")
            break

    # Intel 12th-14th Gen (Alder Lake, Raptor Lake) -> LGA1700
    if any(cpu in product_lower for cpu in ['12th', '13th', '14th', 'i3-12', 'i3-13', 'i3-14',
                                               'i5-12', 'i5-13', 'i5-14',
                                               'i7-12', 'i7-13', 'i7-14',
                                               'i9-12', 'i9-13', 'i9-14']):
        specs['socket'] = 'LGA1700'

    # Intel 10th-11th Gen (Comet Lake, Rocket Lake) -> LGA1200
    elif any(cpu in product_lower for cpu in ['10th', '11th', 'i3-10', 'i3-11',
                                                'i5-10', 'i5-11',
                                                'i7-10', 'i7-11',
                                                'i9-10', 'i9-11']):
        specs['socket'] = 'LGA1200'

    # AMD Ryzen 7000 series -> AM5
    elif any(cpu in product_lower for cpu in ['ryzen 7 7', 'ryzen 5 7', 'ryzen 9 7',
                                                'ryzen 3 7', '7950x', '7900x', '7800x3d',
                                                '7700x', '7600x', '7600']):
        specs['socket'] = 'AM5'

    # AMD Ryzen 5000, 3000, 2000, 1000 series -> AM4
    elif any(cpu in product_lower for cpu in ['ryzen 7 5', 'ryzen 5 5', 'ryzen 9 5',
                                                'ryzen 7 3', 'ryzen 5 3', 'ryzen 9 3',
                                                'ryzen 7 2', 'ryzen 5 2',
                                                'ryzen 7 1', 'ryzen 5 1',
                                                '5950x', '5900x', '5800x3d', '5800x', '5700x', '5600x', '5600',
                                                '3950x', '3900x', '3800x', '3700x', '3600x', '3600']):
        specs['socket'] = 'AM4'

    # AMD Threadripper -> sTRX4 or sTR4
    elif 'threadripper' in product_lower:
        if any(model in product_lower for model in ['3990x', '3970x', '3960x']):
            specs['socket'] = 'sTRX4'
        else:
            specs['socket'] = 'sTR4'

    # 商品名に直接ソケット情報が含まれている場合
    for socket_name, patterns in socket_patterns.items():
        for pattern in patterns:
            if pattern.lower() in product_lower:
                specs['socket'] = socket_name
                break

    return specs


def extract_psu_specs(product_name):
    """電源ユニットの商品名から容量と認証を抽出"""
    specs = {}
    product_lower = product_name.lower()

    # ワット数を抽出（例: 850W, 850ワット, 850watt）
    import re
    wattage_patterns = [
        r'(\d{3,4})\s*w(?:att)?(?:\s|$)',  # 850W, 850watt
        r'(\d{3,4})\s*ワット',              # 850ワット
    ]

    for pattern in wattage_patterns:
        match = re.search(pattern, product_lower)
        if match:
            specs['wattage'] = match.group(1) + 'W'
            print(f"  🔋 検出したワット数: {specs['wattage']}")
            break

    # 80 PLUS認証を抽出
    certifications = {
        '80 PLUS Titanium': ['titanium', 'チタン'],
        '80 PLUS Platinum': ['platinum', 'プラチナ'],
        '80 PLUS Gold': ['gold', 'ゴールド'],
        '80 PLUS Silver': ['silver', 'シルバー'],
        '80 PLUS Bronze': ['bronze', 'ブロンズ'],
        '80 PLUS Standard': ['80 plus standard', '80plus standard'],
    }

    for cert_name, keywords in certifications.items():
        if any(keyword in product_lower for keyword in keywords):
            specs['certification'] = cert_name
            print(f"  🏅 検出した認証: {specs['certification']}")
            break

    # 80 PLUSのみの記載があるか
    if 'certification' not in specs and '80 plus' in product_lower:
        specs['certification'] = '80 PLUS'
        print(f"  🏅 検出した認証: {specs['certification']}")

    return specs


def extract_motherboard_specs(product_name):
    """マザーボードの商品名からスペックを抽出"""
    specs = {}
    product_lower = product_name.lower()

    # ソケット情報
    socket_patterns = {
        'LGA1700': ['lga1700', 'lga 1700'],
        'LGA1200': ['lga1200', 'lga 1200'],
        'AM5': ['am5', 'socket am5'],
        'AM4': ['am4', 'socket am4'],
    }
    for socket_name, patterns in socket_patterns.items():
        if any(p in product_lower for p in patterns):
            specs['socket'] = socket_name
            print(f"  🔌 検出したソケット: {specs['socket']}")
            break

    # チップセット
    chipsets = ['Z790', 'Z690', 'B760', 'B660', 'H770', 'H670', 'X670E', 'X670', 'B650E', 'B650', 'A620', 'X570', 'B550', 'A520']
    for chipset in chipsets:
        if chipset.lower() in product_lower:
            specs['chipset'] = chipset
            print(f"  🔧 検出したチップセット: {specs['chipset']}")
            break

    # フォームファクター
    form_factors = {
        'E-ATX': ['e-atx', 'eatx', 'extended atx'],
        'ATX': ['atx'],
        'Micro-ATX': ['micro-atx', 'matx', 'micro atx'],
        'Mini-ITX': ['mini-itx', 'mini itx', 'mitx'],
    }
    for ff_name, patterns in form_factors.items():
        if any(p in product_lower for p in patterns):
            specs['formFactor'] = ff_name
            print(f"  📐 検出したフォームファクター: {specs['formFactor']}")
            break

    return specs


def extract_memory_specs(product_name):
    """メモリの商品名からスペックを抽出"""
    specs = {}
    product_lower = product_name.lower()
    import re

    # メモリタイプ
    if 'ddr5' in product_lower:
        specs['type'] = 'DDR5'
    elif 'ddr4' in product_lower:
        specs['type'] = 'DDR4'
    if specs.get('type'):
        print(f"  💾 検出したメモリタイプ: {specs['type']}")

    # メモリ速度
    speed_patterns = [
        r'(\d{4,5})\s*mhz',
        r'ddr[45]-(\d{4,5})',
    ]
    for pattern in speed_patterns:
        match = re.search(pattern, product_lower)
        if match:
            specs['speed'] = match.group(1) + 'MHz'
            print(f"  ⚡ 検出したメモリ速度: {specs['speed']}")
            break

    # 容量
    capacity_patterns = [
        r'(\d+)\s*gb',
        r'(\d+)gb',
    ]
    for pattern in capacity_patterns:
        matches = re.findall(pattern, product_lower)
        if matches:
            total = sum(int(m) for m in matches)
            specs['capacity'] = f"{total}GB"
            print(f"  📊 検出したメモリ容量: {specs['capacity']}")
            break

    return specs


def extract_gpu_specs(product_name):
    """GPUの商品名からスペックを抽出"""
    specs = {}
    product_lower = product_name.lower()
    import re

    # 消費電力（TDP/TGP）
    power_patterns = [
        r'(\d{2,3})\s*w(?:att)?(?:\s|$)',
        r'tdp\s*(\d{2,3})',
        r'tgp\s*(\d{2,3})',
    ]
    for pattern in power_patterns:
        match = re.search(pattern, product_lower)
        if match:
            specs['power'] = match.group(1) + 'W'
            print(f"  ⚡ 検出した消費電力: {specs['power']}")
            break

    return specs


def extract_storage_specs(product_name):
    """ストレージの商品名からスペックを抽出"""
    specs = {}
    product_lower = product_name.lower()
    import re

    # ストレージタイプ
    if 'nvme' in product_lower or 'm.2' in product_lower:
        specs['type'] = 'NVMe SSD'
    elif 'ssd' in product_lower and 'sata' in product_lower:
        specs['type'] = 'SATA SSD'
    elif 'ssd' in product_lower:
        specs['type'] = 'SSD'
    elif 'hdd' in product_lower:
        specs['type'] = 'HDD'
    if specs.get('type'):
        print(f"  💿 検出したストレージタイプ: {specs['type']}")

    # 容量
    capacity_patterns = [
        r'(\d+)\s*tb',
        r'(\d+)tb',
        r'(\d+)\s*gb',
        r'(\d+)gb',
    ]
    for pattern in capacity_patterns:
        match = re.search(pattern, product_lower)
        if match:
            capacity = match.group(1)
            if 'tb' in match.group(0):
                specs['capacity'] = capacity + 'TB'
            else:
                specs['capacity'] = capacity + 'GB'
            print(f"  📊 検出した容量: {specs['capacity']}")
            break

    return specs


def extract_case_specs(product_name):
    """PCケースの商品名からスペックを抽出"""
    specs = {}
    product_lower = product_name.lower()

    # フォームファクター
    form_factors = {
        'E-ATX': ['e-atx', 'eatx'],
        'ATX': ['atx'],
        'Micro-ATX': ['micro-atx', 'matx'],
        'Mini-ITX': ['mini-itx', 'mitx'],
    }
    for ff_name, patterns in form_factors.items():
        if any(p in product_lower for p in patterns):
            specs['formFactor'] = ff_name
            print(f"  📐 検出したフォームファクター: {specs['formFactor']}")
            break

    return specs


def extract_cooler_specs(product_name):
    """CPUクーラーの商品名からスペックを抽出"""
    specs = {}
    product_lower = product_name.lower()

    # クーラータイプ
    if '簡易水冷' in product_lower or 'aio' in product_lower or '水冷' in product_lower:
        specs['type'] = '簡易水冷'
    elif '空冷' in product_lower or 'air' in product_lower:
        specs['type'] = '空冷'
    if specs.get('type'):
        print(f"  ❄️ 検出したクーラータイプ: {specs['type']}")

    return specs


def extract_os_specs(product_name):
    """OSの商品名からスペックを抽出"""
    specs = {}
    product_lower = product_name.lower()

    # エディション
    if 'pro' in product_lower:
        specs['edition'] = 'Pro'
    elif 'home' in product_lower:
        specs['edition'] = 'Home'
    if specs.get('edition'):
        print(f"  🏷️ 検出したエディション: {specs['edition']}")

    # ライセンスタイプ
    if 'dsp' in product_lower:
        specs['license'] = 'DSP版'
    elif 'パッケージ' in product_lower or 'package' in product_lower:
        specs['license'] = 'パッケージ版'
    elif 'oem' in product_lower:
        specs['license'] = 'OEM版'
    if specs.get('license'):
        print(f"  📜 検出したライセンス: {specs['license']}")

    return specs


# ==========================
# 🔍 各サイトのスクレイピング関数
# ==========================

def search_kakaku(product_name, category=''):
    """価格.comから最安値を取得（精度向上版）"""
    try:
        # カテゴリに応じて検索クエリを最適化
        search_query = optimize_search_query(product_name, category)
        print(f"🔎 価格.comで検索中: {search_query} (カテゴリ: {category})")

        # 正しいURL形式に修正（価格順にソート）
        # URLエンコーディングを正しく行う
        search_term = quote(search_query, safe='')

        # シンプルな検索URL（ソート指定のみ）
        url = f"https://kakaku.com/search_results/{search_term}/?sort=price_asc"
        print(f"🔗 検索URL: {url}")

        print(f"⏳ 価格.comにリクエスト送信中...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        res = requests.get(url, headers=headers, timeout=15)
        print(f"✅ レスポンス受信完了")

        # レスポンスの文字コードを明示的に設定
        res.encoding = res.apparent_encoding or 'utf-8'

        print(f"📄 HTTPステータス: {res.status_code}")
        print(f"📝 文字コード: {res.encoding}")
        print(f"⏳ HTMLを解析中...")

        soup = BeautifulSoup(res.text, "html.parser")
        print(f"✅ HTML解析完了")

        # 全商品を取得して最安値を探す
        print(f"🔍 商品要素を検索中...")
        items = soup.select(".p-item")
        if not items:
            print(f"  ⏳ .p-itemが見つからず、li.itemを試行中...")
            items = soup.select("li.item")
        if not items:
            print(f"  ⏳ li.itemが見つからず、[data-item]を試行中...")
            items = soup.select("[data-item]")
        if not items:
            print(f"  ⏳ [data-item]が見つからず、.productlist_itemを試行中...")
            items = soup.select(".productlist_item")

        if not items:
            print("❌ 商品要素が見つかりません")
            print(f"📝 検索URL: {url}")
            # HTMLの一部を出力（デバッグ用）
            print(f"📝 HTML冒頭: {str(soup)[:500]}")
            return {}

        print(f"📦 {len(items)}件の商品が見つかりました")
        print(f"⏳ 各商品の価格を解析中...")

        # 価格と商品のリストを作成
        price_list = []

        for idx, item in enumerate(items):
            # 価格の取得（複数パターン試行）
            price_elem = item.select_one(".p-item_price")
            if not price_elem:
                price_elem = item.select_one(".item_price")
            if not price_elem:
                price_elem = item.select_one(".price")
            if not price_elem:
                price_elem = item.select_one("span.priceTxt")
            if not price_elem:
                price_elem = item.select_one(".pryen")

            if price_elem:
                try:
                    price_text = price_elem.get_text(strip=True)
                    # 数字以外を除去して価格を抽出
                    price_num = int(re.sub(r"[^\d]", "", price_text))

                    # 異常値をフィルタリング（0円、または10億円以上は除外）
                    if 100 <= price_num < 1000000000:
                        price_list.append({
                            'price': price_num,
                            'item': item,
                            'index': idx
                        })
                        print(f"  📊 [{idx}] 価格: ¥{price_num:,}")
                except (ValueError, AttributeError) as e:
                    print(f"   [{idx}] 価格解析失敗: {e}")
                    continue

        if not price_list:
            print("❌ 有効な価格が見つかりません")
            return {}

        print(f"✅ {len(price_list)}件の有効な価格を検出")
        print(f"⏳ 価格をソート中...")

        # 価格順にソート
        price_list.sort(key=lambda x: x['price'])

        # 最安値の商品を取得
        best_item_data = price_list[0]
        best_item = best_item_data['item']
        min_price = best_item_data['price']

        print(f"🏆 最安値商品インデックス: {best_item_data['index']}")
        print(f"⏳ 商品情報を抽出中...")

        # 商品名の取得（複数パターン試行）
        name = ""
        name_elem = best_item.select_one(".p-item_name")
        if not name_elem:
            name_elem = best_item.select_one(".item_name")
        if not name_elem:
            name_elem = best_item.select_one("h3")
        if not name_elem:
            name_elem = best_item.select_one("a")
        if not name_elem:
            name_elem = best_item.select_one(".productName")

        if name_elem:
            name = name_elem.get_text(strip=True)
        else:
            # 商品名が見つからない場合は、検索クエリを使用
            name = product_name

        # 画像URLを取得（複数パターン試行）
        image_url = ""
        print(f"🔍 画像URLを検索中...")

        # 複数の画像タグパターンを試行
        img_tag = best_item.select_one("img.p-item_image")
        if not img_tag:
            img_tag = best_item.select_one("img.lazy")
        if not img_tag:
            img_tag = best_item.select_one("img[data-original]")
        if not img_tag:
            img_tag = best_item.select_one("img")

        if img_tag:
            # 複数の属性から画像URLを取得
            image_url = (img_tag.get("data-original") or
                        img_tag.get("data-src") or
                        img_tag.get("data-lazy-src") or
                        img_tag.get("src") or "")

            # 相対URLを絶対URLに変換
            if image_url and not image_url.startswith("http"):
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                elif image_url.startswith("/"):
                    image_url = "https://kakaku.com" + image_url

            # 小さいアイコンやプレースホルダー画像を除外
            if image_url and any(skip in image_url.lower() for skip in ['noimage', 'placeholder', 'loading', '1x1']):
                print(f"  ⚠️ プレースホルダー画像を検出: {image_url}")
                image_url = ""

        # 画像が見つからなかった場合は"No image"
        if not image_url or not image_url.startswith("http"):
            print("⚠️ 価格.comで画像が見つかりませんでした")
            image_url = "No image"
        else:
            print(f"✅ 価格.comから画像取得: {image_url[:60]}...")

        # 型番を商品名から抽出（商品名全体を型番として使用）
        model_number = name

        # CPUの場合はソケット情報を抽出
        result = {
            "price": str(min_price),
            "product": name,
            "source": "価格.com（最安値）",
            "image": image_url,
            "model_number": model_number
        }

        # カテゴリ別のスペック情報を抽出
        print(f"🔍 スペック情報を抽出中...")

        if category == 'cpu':
            cpu_specs = extract_cpu_specs(name)
            result.update(cpu_specs)

        elif category == 'motherboard':
            mb_specs = extract_motherboard_specs(name)
            result.update(mb_specs)

        elif category == 'memory':
            mem_specs = extract_memory_specs(name)
            result.update(mem_specs)

        elif category == 'gpu':
            gpu_specs = extract_gpu_specs(name)
            result.update(gpu_specs)

        elif category == 'storage':
            storage_specs = extract_storage_specs(name)
            result.update(storage_specs)

        elif category == 'psu':
            psu_specs = extract_psu_specs(name)
            result.update(psu_specs)

        elif category == 'case':
            case_specs = extract_case_specs(name)
            result.update(case_specs)

        elif category == 'cooler':
            cooler_specs = extract_cooler_specs(name)
            result.update(cooler_specs)

        elif category == 'os':
            os_specs = extract_os_specs(name)
            result.update(os_specs)

        print(f"✅ 商品名: {name}")
        print(f"✅ 最安値: ¥{min_price:,}円")
        print(f"🖼️ 画像URL: {image_url[:50]}..." if image_url else "🖼️ 画像URL: なし")
        print(f"🎉 価格.comからの取得完了！")

        return result
    except Exception as e:
        print("❌ 価格.com取得失敗:", e)
        import traceback
        traceback.print_exc()
        return {}

def search_rakuten(product_name, category=''):
    """楽天市場から価格を取得"""
    try:
        search_query = optimize_search_query(product_name, category)
        print(f" 楽天で検索中: {search_query}")
        url = f"https://search.rakuten.co.jp/search/mall/{search_query.replace(' ', '+')}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        item = soup.select_one(".searchresultitem")
        if not item:
            return {}

        name = item.select_one(".title").get_text(strip=True)
        price_text = item.select_one(".important").get_text(strip=True)
        price = re.sub(r"[^\d]", "", price_text)

        # 画像URLを取得
        image_url = ""
        img_tag = item.select_one("img")
        if img_tag and img_tag.get("src"):
            image_url = img_tag.get("src")

        # 型番を商品名から抽出
        model_number = name

        return {
            "price": price,
            "product": name,
            "source": "楽天市場",
            "image": image_url,
            "model_number": model_number
        }
    except Exception as e:
        print(" 楽天取得失敗:", e)
        return {}

def search_amazon(product_name, category=''):
    """Amazonから価格を取得"""
    try:
        search_query = optimize_search_query(product_name, category)
        print(f" Amazonで検索中: {search_query}")
        url = f"https://www.amazon.co.jp/s?k={search_query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        item = soup.select_one("div[data-component-type='s-search-result']")
        if not item:
            return {}

        name = item.h2.get_text(strip=True)
        price_text = item.select_one(".a-price-whole")
        if not price_text:
            return {}

        price = re.sub(r"[^\d]", "", price_text.get_text(strip=True))

        # 画像URLを取得
        image_url = ""
        img_tag = item.select_one("img.s-image")
        if img_tag and img_tag.get("src"):
            image_url = img_tag.get("src")

        # 型番を商品名から抽出
        model_number = name

        return {
            "price": price,
            "product": name,
            "source": "Amazon",
            "image": image_url,
            "model_number": model_number
        }
    except Exception as e:
        print(" Amazon取得失敗:", e)
        return {}

def search_google_shopping(product_name, category=''):
    """Googleショッピングから価格を取得"""
    try:
        search_query = optimize_search_query(product_name, category)
        print(f" Googleショッピングで検索中: {search_query}")
        url = f"https://www.google.com/search?tbm=shop&q={search_query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        item = soup.select_one(".sh-dgr__gr-auto")
        if not item:
            return {}

        name = item.select_one(".tAxDx").get_text(strip=True)
        price_text = item.select_one(".a8Pemb").get_text(strip=True)
        price = re.sub(r"[^\d]", "", price_text)

        # 画像URLを取得
        image_url = ""
        img_tag = item.select_one("img")
        if img_tag and img_tag.get("src"):
            image_url = img_tag.get("src")

        # 型番を商品名から抽出
        model_number = name

        return {
            "price": price,
            "product": name,
            "source": "Googleショッピング",
            "image": image_url,
            "model_number": model_number
        }
    except Exception as e:
        print(" Google取得失敗:", e)
        return {}


# ==========================
# 🧩 メイン処理
# ==========================
@app.route('/api/search', methods=['POST'])
def search_product():
    data = request.json
    product_name = data.get('productName', '')
    category = data.get('category', '')

    if not product_name:
        return jsonify({'error': '商品名が必要です'}), 400

    print(f"\n{'='*50}")
    print(f"🔍 検索開始: {product_name} (カテゴリ: {category})")
    print(f"{'='*50}")

    # 価格.comから価格を取得
    web_result = search_kakaku(product_name, category)
    if web_result.get("price"):
        print(f"✅ {web_result['source']} から取得成功: ¥{web_result['price']}円")
        return jsonify(web_result)

    return jsonify({'error': '価格.comで価格を取得できませんでした'}), 404

@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    """入力内容に応じた商品サジェストを取得"""
    data = request.json
    category = data.get('category', '')
    query = data.get('query', '').strip()

    # カテゴリごとの価格.comカテゴリコード
    category_codes = {
        'cpu': '0510',
        'motherboard': '0540',
        'memory': '0520',
        'gpu': '0550',
        'storage': '0537',
        'psu': '0590',
        'case': '0580',
        'cooler': '0512',
        'os': '0560'
    }

    if category not in category_codes:
        return jsonify({'suggestions': []})

    try:
        print(f"\n[SUGGEST] category={category} query={query}")

        suggestions = []

        if query and len(query) >= 2:
            # 入力がある場合は検索結果から取得
            category_code = category_codes[category]

            # カテゴリ別のキーワードフィルター（必須キーワード）
            category_keywords = {
                'cpu': ['Intel', 'AMD', 'Core', 'Ryzen', 'Processor', 'CPU'],
                'motherboard': ['ASUS', 'MSI', 'GIGABYTE', 'ASRock', 'Motherboard', 'マザーボード', 'Z790', 'B760', 'X670', 'B650'],
                'memory': ['DDR4', 'DDR5', 'Memory', 'メモリ', 'RAM', 'GB'],
                'gpu': ['GeForce', 'Radeon', 'グラフィックボード', 'グラフィック', 'ビデオカード', 'GPU', 'NVIDIA', 'AMD', 'RTX', 'GTX', 'RX', 'Arc'],
                'storage': ['SSD', 'HDD', 'NVMe', 'SATA', 'M.2', 'ストレージ'],
                'psu': ['電源', 'PSU', 'Power Supply', '電源ユニット', 'W', '80PLUS'],
                'case': ['ケース', 'PCケース', 'タワー', 'Tower', 'ミドルタワー'],
                'cooler': ['CPUクーラー', 'クーラー', '水冷', '空冷', 'ファン'],
                'os': ['Windows', 'OS', 'オペレーティングシステム']
            }

            # 除外キーワード（これらが含まれていたら除外）
            exclude_keywords = {
                'gpu': ['ウェッジ', 'ゴルフ', 'Golf', 'フレックス', 'ロフト', 'バンス', 'シャフト']
            }

            search_url = f"https://kakaku.com/search_results/{quote(query)}/?category={category_code}"
            print(f"[DEBUG] Search URL: {search_url}")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            res = requests.get(search_url, headers=headers, timeout=10)
            res.encoding = res.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(res.text, "html.parser")

            # 複数のセレクターを試行
            items = soup.select("div.p-item_name a")
            print(f"[DEBUG] p-item_name a: {len(items)}")

            if len(items) == 0:
                items = soup.select("li.item a")
                print(f"[DEBUG] li.item a: {len(items)}")

            if len(items) == 0:
                items = soup.select("a.ckitanker")
                print(f"[DEBUG] a.ckitanker: {len(items)}")

            if len(items) == 0:
                # より一般的なセレクター
                items = soup.select("div[class*='item'] a, td.ckitanker a")
                print(f"[DEBUG] generic selectors: {len(items)}")

            items = items[:10]

            # カテゴリに関連するキーワードを含む商品のみフィルタリング
            keywords = category_keywords.get(category, [])
            excludes = exclude_keywords.get(category, [])

            for item in items:
                name = item.get_text(strip=True)
                name = name.replace('\n', ' ').replace('  ', ' ').strip()

                # 除外キーワードチェック
                is_excluded = False
                for exclude in excludes:
                    if exclude in name:
                        is_excluded = True
                        print(f"[DEBUG] Excluded (contains '{exclude}'): {name}")
                        break

                if is_excluded:
                    continue

                # PCパーツに関連するキーワードが含まれているかチェック
                is_relevant = False
                if keywords:
                    for keyword in keywords:
                        if keyword.lower() in name.lower():
                            is_relevant = True
                            break
                else:
                    is_relevant = True  # キーワードがない場合はすべて許可

                if name and len(name) > 3 and name not in suggestions and is_relevant:
                    suggestions.append(name)
                    print(f"[DEBUG] Added: {name}")

        else:
            # 入力がない場合は人気商品の例を返す
            popular_items = {
                'cpu': ['Intel Core i9-14900K', 'AMD Ryzen 9 7950X', 'Intel Core i7-14700K', 'AMD Ryzen 7 7800X3D'],
                'motherboard': ['ASUS ROG MAXIMUS Z790', 'MSI MPG B650 EDGE WIFI', 'ASUS TUF GAMING B760M'],
                'memory': ['DDR5-6000 32GB', 'DDR4-3200 16GB', 'DDR5-5600 32GB'],
                'gpu': ['RTX 4090', 'RTX 4080 SUPER', 'RTX 4070 Ti SUPER', 'RX 7900 XTX'],
                'storage': ['Samsung 990 PRO 2TB', 'WD Blue SN580 1TB', 'Crucial P3 Plus 2TB'],
                'psu': ['Corsair RM850e 850W', 'Seasonic FOCUS GX-850 850W'],
                'case': ['NZXT H9 Flow', 'Fractal Design Pop Air RGB'],
                'cooler': ['Noctua NH-D15', 'DeepCool AK620'],
                'os': ['Windows 11 Home', 'Windows 11 Pro']
            }

            suggestions = popular_items.get(category, [])

        print(f"✅ {len(suggestions)}件のサジェストを取得")
        return jsonify({'suggestions': suggestions[:8]})

    except Exception as e:
        print(f"❌ サジェスト取得失敗: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'suggestions': []})

@app.route('/')
def index():
    """メインページを表示"""
    return send_from_directory('static', 'index.html')

# ==========================
# 🖥️ サーバー起動
# ==========================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("  💻 Web価格自動取得サーバー")
    print("="*60)
    print("📡 価格.com から自動取得")
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 起動中: http://localhost:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=True)
