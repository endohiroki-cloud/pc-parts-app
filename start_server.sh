#!/bin/bash

echo "================================================"
echo "  価格.com自動取得サーバー 起動スクリプト"
echo "================================================"
echo ""

# Pythonが利用可能かチェック
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ エラー: Pythonがインストールされていません"
    echo "   Pythonをインストールしてください"
    exit 1
fi

echo "✅ Python検出: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# 必要なパッケージのチェック
echo "📦 必要なパッケージをチェック中..."
MISSING_PACKAGES=()

for package in flask flask-cors requests beautifulsoup4; do
    if ! $PYTHON_CMD -c "import ${package//-/_}" 2>/dev/null; then
        MISSING_PACKAGES+=($package)
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "⚠️  以下のパッケージがインストールされていません:"
    for pkg in "${MISSING_PACKAGES[@]}"; do
        echo "   - $pkg"
    done
    echo ""
    echo "インストールしますか? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "📥 パッケージをインストール中..."
        $PYTHON_CMD -m pip install "${MISSING_PACKAGES[@]}"
    else
        echo "❌ 必要なパッケージがないため起動できません"
        exit 1
    fi
fi

echo "✅ すべてのパッケージが揃っています"
echo ""

# サーバーファイルの存在確認
if [ ! -f "scraper.py" ]; then
    echo "❌ エラー: scraper.pyが見つかりません"
    echo "   このスクリプトと同じディレクトリにscraper.pyを配置してください"
    exit 1
fi

echo "🚀 サーバーを起動しています..."
echo ""
echo "サーバーが起動したら:"
echo "  1. ブラウザでpc-parts-selector-auto.htmlを開く"
echo "  2. 製品名を入力してボタンをクリック"
echo "  3. 価格が自動取得されます！"
echo ""
echo "サーバーを停止するには: Ctrl+C"
echo ""
echo "================================================"
echo ""

# サーバー起動
$PYTHON_CMD scraper.py
