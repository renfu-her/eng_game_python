from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from models import GameRoom, GameSession, RoomQuestion, Question, User
from marshmallow import Schema, fields, ValidationError
from datetime import datetime
import random

room_bp = Blueprint('rooms', __name__)

class RoomCreateSchema(Schema):
    """房間建立驗證 Schema"""
    name = fields.Str(required=True, validate=lambda x: len(x) >= 3)
    max_players = fields.Int(required=False, validate=lambda x: 2 <= x <= 20)
    total_rounds = fields.Int(required=False, validate=lambda x: 1 <= x <= 50)
    categories = fields.List(fields.Str(), required=True, validate=lambda x: len(x) > 0)

@room_bp.route('/', methods=['POST'])
@jwt_required()
def create_room():
    """建立遊戲房間"""
    try:
        schema = RoomCreateSchema()
        data = schema.load(request.get_json())
        user_id = get_jwt_identity()
        
        # 建立房間
        room = GameRoom(
            name=data['name'],
            max_players=data.get('max_players', 10),
            total_rounds=data.get('total_rounds', 10),
            categories=data['categories'],
            created_by=user_id
        )
        
        db.session.add(room)
        db.session.commit()
        
        # 自動加入房間
        session = GameSession(
            user_id=user_id,
            room_id=room.id
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': '房間建立成功',
            'room': room.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': '驗證錯誤', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '建立房間失敗'}), 500

@room_bp.route('/', methods=['GET'])
def get_rooms():
    """取得房間列表"""
    try:
        status = request.args.get('status', 'waiting')
        limit = request.args.get('limit', type=int, default=20)
        
        query = GameRoom.query.filter_by(status=status)
        rooms = query.order_by(GameRoom.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'rooms': [room.to_dict() for room in rooms],
            'total': len(rooms)
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得房間列表失敗'}), 500

@room_bp.route('/<room_id>', methods=['GET'])
def get_room(room_id):
    """取得房間詳細資訊"""
    try:
        room = GameRoom.query.get(room_id)
        
        if not room:
            return jsonify({'error': '房間不存在'}), 404
        
        # 取得玩家資訊
        players = []
        for session in room.players:
            user = User.query.get(session.user_id)
            if user:
                player_info = session.to_dict()
                player_info['username'] = user.username
                players.append(player_info)
        
        room_data = room.to_dict()
        room_data['players'] = players
        
        return jsonify({
            'room': room_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得房間資訊失敗'}), 500

@room_bp.route('/<room_id>/join', methods=['POST'])
@jwt_required()
def join_room(room_id):
    """加入遊戲房間"""
    try:
        user_id = get_jwt_identity()
        room = GameRoom.query.get(room_id)
        
        if not room:
            return jsonify({'error': '房間不存在'}), 404
        
        if room.status != 'waiting':
            return jsonify({'error': '房間已開始遊戲'}), 400
        
        if len(room.players) >= room.max_players:
            return jsonify({'error': '房間已滿'}), 400
        
        # 檢查是否已在房間中
        existing_session = GameSession.query.filter_by(
            user_id=user_id, 
            room_id=room_id
        ).first()
        
        if existing_session:
            return jsonify({'error': '已在房間中'}), 400
        
        # 建立遊戲會話
        session = GameSession(
            user_id=user_id,
            room_id=room_id
        )
        
        db.session.add(session)
        db.session.commit()
        
        # 透過 WebSocket 通知其他玩家
        socketio.emit('player_joined', {
            'user_id': user_id,
            'username': User.query.get(user_id).username
        }, room=room_id)
        
        return jsonify({
            'message': '成功加入房間',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '加入房間失敗'}), 500

@room_bp.route('/<room_id>/start', methods=['POST'])
@jwt_required()
def start_game(room_id):
    """開始遊戲"""
    try:
        user_id = get_jwt_identity()
        room = GameRoom.query.get(room_id)
        
        if not room:
            return jsonify({'error': '房間不存在'}), 404
        
        if room.created_by != user_id:
            return jsonify({'error': '只有房主可以開始遊戲'}), 403
        
        if room.status != 'waiting':
            return jsonify({'error': '遊戲已開始'}), 400
        
        if len(room.players) < 2:
            return jsonify({'error': '至少需要 2 名玩家'}), 400
        
        # 取得題目
        questions = Question.query.filter(
            Question.category.in_(room.categories)
        ).order_by(db.func.random()).limit(room.total_rounds).all()
        
        if len(questions) < room.total_rounds:
            return jsonify({'error': '題目數量不足'}), 400
        
        # 建立房間題目關聯
        for i, question in enumerate(questions):
            room_question = RoomQuestion(
                room_id=room.id,
                question_id=question.id,
                round_number=i + 1,
                order_in_round=1
            )
            db.session.add(room_question)
        
        # 更新房間狀態
        room.status = 'in_progress'
        room.started_at = datetime.utcnow()
        room.current_round = 1
        
        db.session.commit()
        
        # 透過 WebSocket 通知遊戲開始
        socketio.emit('game_started', {
            'room_id': room.id,
            'total_rounds': room.total_rounds
        }, room=room_id)
        
        return jsonify({
            'message': '遊戲開始',
            'room': room.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '開始遊戲失敗'}), 500

@room_bp.route('/<room_id>/leave', methods=['POST'])
@jwt_required()
def leave_room(room_id):
    """離開房間"""
    try:
        user_id = get_jwt_identity()
        session = GameSession.query.filter_by(
            user_id=user_id, 
            room_id=room_id
        ).first()
        
        if not session:
            return jsonify({'error': '不在房間中'}), 400
        
        session.left_at = datetime.utcnow()
        db.session.commit()
        
        # 透過 WebSocket 通知其他玩家
        socketio.emit('player_left', {
            'user_id': user_id,
            'username': User.query.get(user_id).username
        }, room=room_id)
        
        return jsonify({
            'message': '成功離開房間'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '離開房間失敗'}), 500 