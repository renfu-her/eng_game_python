@echo off
setlocal enabledelayedexpansion

echo 🚀 英文對答遊戲部署腳本
echo ================================

REM 檢查虛擬環境
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  建議在虛擬環境中運行
    set /p "continue=是否繼續？(y/N): "
    if /i not "!continue!"=="y" exit /b 1
)

REM 停止現有服務
echo 🛑 停止現有服務...
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq gunicorn*" >nul 2>&1
if %errorlevel% equ 0 (
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq gunicorn*" >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo ✅ 服務已停止
) else (
    echo ℹ️  沒有運行中的服務
)

REM 更新程式碼（如果使用 Git）
if exist ".git" (
    echo 📥 更新程式碼...
    git pull origin main
    echo ✅ 程式碼已更新
)

REM 安裝/更新依賴
echo 📦 安裝依賴套件...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依賴安裝失敗
    pause
    exit /b 1
)
echo ✅ 依賴套件已安裝

REM 初始化資料庫
echo 🗄️ 初始化資料庫...
python init_db.py
if %errorlevel% neq 0 (
    echo ❌ 資料庫初始化失敗
    pause
    exit /b 1
)
echo ✅ 資料庫已初始化

REM 建立日誌目錄
echo 📁 建立日誌目錄...
if not exist "logs" mkdir logs
echo ✅ 日誌目錄已建立

REM 啟動服務
echo 🚀 啟動服務...
echo 📡 伺服器地址: http://localhost:5000
echo 🔌 WebSocket 地址: ws://localhost:5000
echo 📚 測試頁面: http://localhost:5000/public/index.html
echo ⏹️  按 Ctrl+C 停止伺服器
echo ================================

REM 使用 Gunicorn 啟動
python -m gunicorn -c gunicorn.conf.py "app:create_app()"

pause 