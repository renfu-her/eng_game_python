#!/usr/bin/env python3
"""
英文遊戲生產環境啟動腳本
使用 Gunicorn 作為 WSGI 伺服器
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """檢查必要條件"""
    print("🔍 檢查系統環境...")
    
    # 檢查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        return False
    
    # 檢查虛擬環境
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  建議在虛擬環境中運行")
    
    # 檢查必要套件
    try:
        import flask
        import flask_socketio
        import flask_sqlalchemy
        import pymysql
        print("✅ 必要套件檢查通過")
    except ImportError as e:
        print(f"❌ 缺少必要套件: {e}")
        print("請執行: pip install -r requirements.txt")
        return False
    
    return True

def create_gunicorn_config():
    """建立 Gunicorn 配置檔案"""
    config_content = '''# Gunicorn 配置檔案
bind = "0.0.0.0:5000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
capture_output = True
'''
    
    config_path = Path("gunicorn.conf.py")
    if not config_path.exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Gunicorn 配置檔案已建立")
    else:
        print("ℹ️  Gunicorn 配置檔案已存在")

def create_logs_directory():
    """建立日誌目錄"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ 日誌目錄已建立")
    else:
        print("ℹ️  日誌目錄已存在")

def install_gunicorn():
    """安裝 Gunicorn"""
    try:
        import gunicorn
        print("✅ Gunicorn 已安裝")
    except ImportError:
        print("📦 安裝 Gunicorn...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn[gevent]"])
            print("✅ Gunicorn 安裝成功")
        except subprocess.CalledProcessError:
            print("❌ Gunicorn 安裝失敗")
            return False
    return True

def start_gunicorn():
    """啟動 Gunicorn"""
    print("🚀 啟動生產環境伺服器...")
    print("📡 伺服器地址: http://localhost:5000")
    print("🔌 WebSocket 地址: ws://localhost:5000")
    print("📚 測試頁面: http://localhost:5000/public/index.html")
    print("⏹️  按 Ctrl+C 停止伺服器")
    print("-" * 50)
    
    try:
        # 啟動 Gunicorn
        subprocess.run([
            sys.executable, "-m", "gunicorn",
            "-c", "gunicorn.conf.py",
            "app:create_app()"
        ])
    except KeyboardInterrupt:
        print("\n🛑 伺服器已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        return False
    
    return True

def main():
    """主函式"""
    print("🎮 英文對答遊戲 - 生產環境啟動")
    print("=" * 50)
    
    # 設定環境變數
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # 檢查必要條件
    if not check_requirements():
        sys.exit(1)
    
    # 建立配置檔案
    create_gunicorn_config()
    create_logs_directory()
    
    # 安裝 Gunicorn
    if not install_gunicorn():
        sys.exit(1)
    
    # 啟動伺服器
    if not start_gunicorn():
        sys.exit(1)

if __name__ == '__main__':
    main() 