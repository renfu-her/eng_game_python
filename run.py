#!/usr/bin/env python3
"""
英文遊戲應用程式啟動腳本
"""

import os
import sys
from app import create_app, socketio

def main():
    """主啟動函式"""
    # 設定環境變數
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # 建立應用程式
    app = create_app()
    
    print("🎮 英文對答遊戲啟動中...")
    print("📡 伺服器地址: http://localhost:5000")
    print("🔌 WebSocket 地址: ws://localhost:5000")
    print("📚 API 文件: http://localhost:5000/api/")
    print("⏹️  按 Ctrl+C 停止伺服器")
    print("-" * 50)
    
    try:
        # 啟動伺服器
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n🛑 伺服器已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 