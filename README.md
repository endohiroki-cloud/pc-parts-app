# 🖥️ 自作PCパーツ選定アプリ

価格.comから最安値を自動取得できる自作PCパーツ管理アプリです。

---

## 📦 ファイル一覧

### メインアプリ
- **pc-parts-selector-auto.html** - 価格自動取得版（サーバー必要）
- **pc-parts-selector-complete.html** - スタンドアローン版（サーバー不要）

### サーバー関連
- **scraper.py** - 価格.com自動取得サーバー
- **start_server.sh** - サーバー起動スクリプト（Linux/macOS）
- **start_server.bat** - サーバー起動スクリプト（Windows）

### ドキュメント
- **SERVER_START_GUIDE.md** - サーバー起動の詳細ガイド
- **README.md** - このファイル

---

## 🚀 クイックスタート

### 方法1: 完全自動版（おすすめ）

**Windows:**
1. `start_server.bat` をダブルクリック
2. ブラウザで `pc-parts-selector-auto.html` を開く
3. 完了！

**Mac/Linux:**
```bash
chmod +x start_server.sh
./start_server.sh
```
その後、ブラウザで `pc-parts-selector-auto.html` を開く

### 方法2: スタンドアローン版（サーバー不要）

1. ブラウザで `pc-parts-selector-complete.html` を開く
2. 完了！（価格は手動入力）

---

## ✨ 機能

### 完全自動版（pc-parts-selector-auto.html）
- ✅ 価格.comから最安値を自動取得
- ✅ スペック情報を自動入力
- ✅ 商品画像を自動取得
- ✅ 互換性チェック
- ✅ 合計金額の自動計算

### スタンドアローン版（pc-parts-selector-complete.html）
- ✅ スペック情報を自動入力
- ✅ 互換性チェック
- ✅ 合計金額の自動計算
- ⚠️ 価格は手動入力

---

## 📝 使い方

### 基本的な流れ

1. **製品名を入力**
   ```
   例: Core i7-14700K
   例: RTX 4070 Ti
   例: Corsair Vengeance DDR5 32GB
   ```

2. **🏷️ ボタンをクリック**
   - 価格.comが開きます（参考用）
   - 自動版：価格が自動で入力されます
   - 手動版：価格.comで確認して手動入力

3. **スペック確認**
   - ソケット、TDP、容量などが自動入力されます
   - 必要に応じて修正

4. **保存**
   - 💾 テキストファイルで保存ボタンをクリック

---

## 🎯 対応パーツ

- 🔲 CPU
- 🔌 マザーボード  
- 💾 メモリ
- 🎮 グラフィックボード
- 💿 ストレージ
- ⚡ 電源ユニット
- 📦 PCケース
- ❄️ CPUクーラー
- 💻 OS

---

## 🔧 サーバー起動方法（自動版を使う場合）

### 簡単な方法

**Windows:**
```
start_server.bat をダブルクリック
```

**Mac/Linux:**
```bash
./start_server.sh
```

### 手動で起動

1. **必要なパッケージをインストール:**
```bash
pip install flask flask-cors requests beautifulsoup4
```

2. **サーバーを起動:**
```bash
python scraper.py
```

3. **起動確認:**
```
* Running on http://127.0.0.1:5000
```
このメッセージが表示されればOK！

詳細は `SERVER_START_GUIDE.md` を参照してください。

---

## ⚙️ システム要件

### 完全自動版
- Python 3.7以上
- 必要なPythonパッケージ（自動インストール可能）
- モダンなWebブラウザ

### スタンドアローン版
- モダンなWebブラウザのみ

---

## 🆘 トラブルシューティング

### Q: サーバーが起動しない
**A:** `SERVER_START_GUIDE.md` のトラブルシューティングセクションを参照

### Q: 価格が自動取得されない
**A:** 以下を確認してください：
1. サーバーが起動しているか
2. `http://localhost:5000` にアクセスできるか
3. ブラウザのコンソールにエラーがないか

### Q: サーバーなしで使いたい
**A:** `pc-parts-selector-complete.html` を使用してください

---

## 📋 サポートされている製品例

### CPU
- Intel: Core i7-14700K, Core i5-14600K
- AMD: Ryzen 7 7800X3D, Ryzen 9 7950X

### GPU
- NVIDIA: RTX 4090, RTX 4080, RTX 4070 Ti, RTX 4070
- AMD: RX 7900 XTX, RX 7900 XT

### その他
主要なPC部品メーカーの製品に対応

---

## ⚠️ 注意事項

- 価格情報は参考価格です。実際の価格は価格.comで確認してください
- サーバーは開発用です。本番環境での使用は推奨されません
- 価格.comの利用規約を遵守してください

---

## 🔄 更新履歴

### v2.0 (最新)
- ✨ 価格.com自動取得機能を追加
- ✨ OSセクションを追加
- 🔧 スペック自動抽出の精度向上
- 📝 起動スクリプトを追加

### v1.0
- 🎉 初回リリース
- ✅ 基本的なパーツ管理機能

---

## 💡 ヒント

- 製品名は正確に入力すると自動入力の精度が上がります
- 型番を含めると検索精度が向上します（例：RTX 4070 Ti）
- 互換性チェック機能を活用しましょう

---

## 📞 サポート

問題が発生した場合：
1. `SERVER_START_GUIDE.md` を確認
2. ブラウザのコンソールでエラーを確認
3. サーバーのログを確認

---

🎮 Happy PC Building! 🎮
