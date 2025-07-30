from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

# 初始化擴充套件
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()

def create_app(config_name=None):
    """應用程式工廠函式"""
    app = Flask(__name__)
    
    # 載入設定
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(f'config.{config_name.capitalize()}Config')
    
    # 初始化擴充套件
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # 註冊藍圖
    from blueprints.auth_routes import auth_bp
    from blueprints.question_routes import question_bp
    from blueprints.room_routes import room_bp
    from blueprints.game_routes import game_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(question_bp, url_prefix='/api/questions')
    app.register_blueprint(room_bp, url_prefix='/api/rooms')
    app.register_blueprint(game_bp, url_prefix='/api/game')
    
    # 導入 WebSocket 事件
    import socket_events
    
    # 靜態檔案路由
    @app.route('/<path:filename>')
    def public_files(filename):
        return send_from_directory('public', filename)

    @app.route('/')
    def index():
        return send_from_directory('public', 'index.html')

    @app.route('/admin')
    def admin():
        return send_from_directory('public', 'admin.html')
    
    # 錯誤處理
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 