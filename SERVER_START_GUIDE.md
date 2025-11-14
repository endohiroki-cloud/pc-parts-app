# 価格.com自動取得サーバー 起動ガイド

## 📋 必要なもの

1. Python 3.7以上
2. 必要なPythonパッケージ
   - Flask
   - flask-cors
   - requests
   - beautifulsoup4

---

## 🚀 起動手順

### ステップ1: 必要なパッケージをインストール

Windowsの場合：
```bash
pip install flask flask-cors requests beautifulsoup4
```

macOS/Linuxの場合：
```bash
pip3 install flask flask-cors requests beautifulsoup4
```

### ステップ2: サーバーファイルの場所を確認

サーバーファイル（`scraper.py`）は以下の場所にあります：
```
/home/claude/scraper.py
```

### ステップ3: サーバーを起動

**方法1: コマンドラインから起動（推奨）**

ターミナル/コマンドプロンプトを開いて：

```bash
cd /home/claude
python3 scraper.py
```

または

```bash
cd /home/claude
python scraper.py
```

### ステップ4: 起動確認

サーバーが正常に起動すると、以下のようなメッセージが表示されます：

```
 * Serving Flask app 'scraper'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Running on http://XXX.XXX.XXX.XXX:5000
Press CTRL+C to quit
```

このメッセージが表示されれば起動成功です！

---

## ✅ 動作確認

### ブラウザで確認

別のターミナル/コマンドプロンプトを開いて：

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"productName":"Core i7-14700K","category":"cpu"}'
```

または、ブラウザで `http://localhost:5000` にアクセスして確認できます。

---

## 🔧 トラブルシューティング

### エラー1: "command not found: python3"

**解決策:**
```bash
python scraper.py
```
（python3の代わりにpythonを使う）

### エラー2: "ModuleNotFoundError: No module named 'flask'"

**解決策:**
```bash
pip install flask flask-cors requests beautifulsoup4
```
または
```bash
pip3 install flask flask-cors requests beautifulsoup4
```

### エラー3: "Address already in use"

**原因:** すでにサーバーが起動しています

**解決策:**
```bash
# 既存のプロセスを確認
ps aux | grep python | grep scraper

# プロセスを終了（プロセスIDを確認して）
kill [プロセスID]
```

### エラー4: ポート5000が使えない

**解決策:** サーバーファイルの最後の行を編集：
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # ポートを8080に変更
```

---

## 🌐 アプリの使い方（サーバー起動後）

1. サーバーが起動していることを確認
2. `pc-parts-selector-auto.html` をブラウザで開く
3. 製品名を入力（例：Core i7-14700K）
4. 🏷️ボタンをクリック
5. 価格が自動で入力されます！

---

## 🛑 サーバーの停止方法

サーバーを起動したターミナルで：
```
Ctrl + C
```

---

## 📝 バックグラウンドで起動（Linux/macOS）

サーバーをバックグラウンドで起動したい場合：

```bash
cd /home/claude
nohup python3 scraper.py > server.log 2>&1 &
```

停止する場合：
```bash
ps aux | grep scraper.py
kill [プロセスID]
```

---

## ⚠️ 注意事項

- サーバーを起動したままブラウザでアプリを使用してください
- サーバーを停止すると価格の自動取得ができなくなります
- 開発用サーバーのため、本番環境での使用は推奨されません

---

## 💡 代替案（サーバーなし）

サーバーの起動が難しい場合は、以下のファイルを使用してください：

**pc-parts-selector-complete.html**
- サーバー不要
- スペック情報は自動入力
- 価格は価格.comで確認して手動入力

---

## 🆘 それでも起動しない場合

以下の情報を確認してください：

1. Pythonのバージョン
```bash
python --version
```

2. インストール済みパッケージ
```bash
pip list | grep -E "flask|requests|beautifulsoup"
```

3. エラーメッセージの全文をコピー

これらの情報があれば、問題を特定しやすくなります。
