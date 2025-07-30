#!/bin/bash

echo "🎮 英文對答遊戲啟動腳本"
echo "================================"

echo "📦 檢查 Python 環境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝"
    exit 1
fi

python3 --version

echo "📦 檢查虛擬環境..."
if [ ! -d "venv" ]; then
    echo "🔧 建立虛擬環境..."
    python3 -m venv venv
fi

echo "🔧 啟動虛擬環境..."
source venv/bin/activate

echo "📦 安裝依賴套件..."
pip install -r requirements.txt

echo "🗄️ 初始化資料庫..."
python init_db.py

echo "🚀 啟動應用程式..."
echo "📡 伺服器地址: http://localhost:5000"
echo "🔌 WebSocket 地址: ws://localhost:5000"
echo "📚 測試頁面: http://localhost:5000/public/index.html"
echo "⏹️  按 Ctrl+C 停止伺服器"
echo "================================"

python run.py 