@echo off
chcp 65001 > nul
echo ================================================
echo   価格.com自動取得サーバー 起動スクリプト
echo ================================================
echo.

REM Pythonが利用可能かチェック
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ エラー: Pythonがインストールされていません
    echo    https://www.python.org/ からPythonをインストールしてください
    pause
    exit /b 1
)

echo ✅ Python検出
python --version
echo.

REM 必要なパッケージのチェックとインストール
echo 📦 必要なパッケージをチェック中...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  必要なパッケージがインストールされていません
    echo 📥 パッケージをインストール中...
    python -m pip install flask flask-cors requests beautifulsoup4
    if %errorlevel% neq 0 (
        echo ❌ パッケージのインストールに失敗しました
        pause
        exit /b 1
    )
)

echo ✅ すべてのパッケージが揃っています
echo.

REM サーバーファイルの存在確認
if not exist "scraper.py" (
    echo ❌ エラー: scraper.pyが見つかりません
    echo    このスクリプトと同じフォルダにscraper.pyを配置してください
    pause
    exit /b 1
)

echo 🚀 サーバーを起動しています...
echo.
echo サーバーが起動したら:
echo   1. ブラウザでpc-parts-selector-auto.htmlを開く
echo   2. 製品名を入力してボタンをクリック
echo   3. 価格が自動取得されます！
echo.
echo サーバーを停止するには: Ctrl+C
echo.
echo ================================================
echo.

REM サーバー起動
python scraper.py

pause
