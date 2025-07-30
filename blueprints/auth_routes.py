from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import User
from marshmallow import Schema, fields, ValidationError

auth_bp = Blueprint('auth', __name__)

class UserRegistrationSchema(Schema):
    """使用者註冊驗證 Schema"""
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)

class UserLoginSchema(Schema):
    """使用者登入驗證 Schema"""
    username = fields.Str(required=True)
    password = fields.Str(required=True)

@auth_bp.route('/register', methods=['POST'])
def register():
    """使用者註冊"""
    try:
        schema = UserRegistrationSchema()
        data = schema.load(request.get_json())
        
        # 檢查使用者名稱是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '使用者名稱已存在'}), 400
        
        # 檢查電子郵件是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '電子郵件已存在'}), 400
        
        # 建立新使用者
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '註冊成功',
            'user': user.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': '驗證錯誤', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        print(f'註冊失敗錯誤: {e}')
        return jsonify({'error': '註冊失敗'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """使用者登入"""
    try:
        schema = UserLoginSchema()
        data = schema.load(request.get_json())
        
        # 查找使用者
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': '使用者名稱或密碼錯誤'}), 401
        
        # 建立 JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': '登入成功',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': '驗證錯誤', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': '登入失敗'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """取得當前使用者資訊"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '使用者不存在'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得使用者資訊失敗'}), 500 