#!/bin/bash

# 🚀 英文對答遊戲部署腳本
# 適用於純 Python 環境

set -e  # 遇到錯誤立即退出

echo "🎮 英文對答遊戲部署腳本"
echo "================================"

# 檢查是否在虛擬環境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  建議在虛擬環境中運行"
    read -p "是否繼續？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 停止現有服務（如果存在）
echo "🛑 停止現有服務..."
if pgrep -f "gunicorn.*app:create_app" > /dev/null; then
    pkill -f "gunicorn.*app:create_app"
    sleep 2
    echo "✅ 服務已停止"
else
    echo "ℹ️  沒有運行中的服務"
fi

# 更新程式碼（如果使用 Git）
if [ -d ".git" ]; then
    echo "📥 更新程式碼..."
    git pull origin main
    echo "✅ 程式碼已更新"
fi

# 安裝/更新依賴
echo "📦 安裝依賴套件..."
pip install -r requirements.txt
echo "✅ 依賴套件已安裝"

# 初始化資料庫
echo "🗄️ 初始化資料庫..."
python init_db.py
echo "✅ 資料庫已初始化"

# 建立日誌目錄
echo "📁 建立日誌目錄..."
mkdir -p logs
echo "✅ 日誌目錄已建立"

# 啟動服務
echo "🚀 啟動服務..."
echo "📡 伺服器地址: http://localhost:5000"
echo "🔌 WebSocket 地址: ws://localhost:5000"
echo "📚 測試頁面: http://localhost:5000/public/index.html"
echo "⏹️  按 Ctrl+C 停止伺服器"
echo "================================"

# 使用 Gunicorn 啟動
python -m gunicorn -c gunicorn.conf.py "app:create_app()" 