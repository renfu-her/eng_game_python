from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from models import GameRoom, GameSession, RoomQuestion, PlayerAnswer, Question, User
from marshmallow import Schema, fields, ValidationError
from datetime import datetime
import time

game_bp = Blueprint('game', __name__)

class AnswerSubmitSchema(Schema):
    """答案提交驗證 Schema"""
    answer = fields.Raw(required=True)  # 可以是字串或列表
    time_taken = fields.Float(required=True, validate=lambda x: x >= 0)

@game_bp.route('/<room_id>/current-question', methods=['GET'])
@jwt_required()
def get_current_question(room_id):
    """取得當前題目"""
    try:
        user_id = get_jwt_identity()
        room = GameRoom.query.get(room_id)
        
        if not room:
            return jsonify({'error': '房間不存在'}), 404
        
        if room.status != 'in_progress':
            return jsonify({'error': '遊戲未進行中'}), 400
        
        # 取得當前題目
        current_question = RoomQuestion.query.filter_by(
            room_id=room_id,
            round_number=room.current_round
        ).first()
        
        if not current_question:
            return jsonify({'error': '題目不存在'}), 404
        
        # 檢查是否已回答
        existing_answer = PlayerAnswer.query.filter_by(
            session_id=GameSession.query.filter_by(user_id=user_id, room_id=room_id).first().id,
            room_question_id=current_question.id
        ).first()
        
        question_data = current_question.question.to_dict()
        question_data['room_question_id'] = current_question.id
        question_data['time_limit'] = current_question.time_limit
        question_data['answered'] = existing_answer is not None
        
        return jsonify({
            'question': question_data,
            'current_round': room.current_round,
            'total_rounds': room.total_rounds
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得題目失敗'}), 500

@game_bp.route('/<room_id>/submit-answer', methods=['POST'])
@jwt_required()
def submit_answer(room_id):
    """提交答案"""
    try:
        user_id = get_jwt_identity()
        schema = AnswerSubmitSchema()
        data = schema.load(request.get_json())
        
        room = GameRoom.query.get(room_id)
        if not room or room.status != 'in_progress':
            return jsonify({'error': '遊戲未進行中'}), 400
        
        session = GameSession.query.filter_by(user_id=user_id, room_id=room_id).first()
        if not session:
            return jsonify({'error': '不在遊戲中'}), 400
        
        # 取得當前題目
        current_question = RoomQuestion.query.filter_by(
            room_id=room_id,
            round_number=room.current_round
        ).first()
        
        if not current_question:
            return jsonify({'error': '題目不存在'}), 404
        
        # 檢查是否已回答
        existing_answer = PlayerAnswer.query.filter_by(
            session_id=session.id,
            room_question_id=current_question.id
        ).first()
        
        if existing_answer:
            return jsonify({'error': '已回答此題'}), 400
        
        # 驗證答案
        question = current_question.question
        is_correct = False
        
        if question.question_type == 'multiple_choice':
            is_correct = data['answer'] == question.answer
        elif question.question_type == 'multi_blank':
            is_correct = data['answer'] == question.answer
        
        # 儲存答案
        player_answer = PlayerAnswer(
            session_id=session.id,
            room_question_id=current_question.id,
            answer=data['answer'],
            is_correct=is_correct,
            time_taken=data['time_taken']
        )
        
        db.session.add(player_answer)
        
        # 更新會話統計
        session.total_answers += 1
        if is_correct:
            session.correct_answers += 1
            session.score += max(1, int(30 - data['time_taken']))  # 根據答題時間給分
        
        db.session.commit()
        
        # 透過 WebSocket 通知其他玩家
        socketio.emit('answer_submitted', {
            'user_id': user_id,
            'username': User.query.get(user_id).username,
            'is_correct': is_correct,
            'time_taken': data['time_taken']
        }, room=room_id)
        
        return jsonify({
            'message': '答案提交成功',
            'is_correct': is_correct,
            'correct_answer': question.answer,
            'explanation': question.explanation
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': '驗證錯誤', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '提交答案失敗'}), 500

@game_bp.route('/<room_id>/next-round', methods=['POST'])
@jwt_required()
def next_round(room_id):
    """進入下一回合"""
    try:
        user_id = get_jwt_identity()
        room = GameRoom.query.get(room_id)
        
        if not room or room.created_by != user_id:
            return jsonify({'error': '權限不足'}), 403
        
        if room.status != 'in_progress':
            return jsonify({'error': '遊戲未進行中'}), 400
        
        # 檢查所有玩家是否都已答題
        current_question = RoomQuestion.query.filter_by(
            room_id=room_id,
            round_number=room.current_round
        ).first()
        
        if not current_question:
            return jsonify({'error': '題目不存在'}), 404
        
        answered_count = PlayerAnswer.query.filter_by(
            room_question_id=current_question.id
        ).count()
        
        if answered_count < len(room.players):
            return jsonify({'error': '還有玩家未答題'}), 400
        
        # 進入下一回合或結束遊戲
        if room.current_round >= room.total_rounds:
            # 遊戲結束
            room.status = 'finished'
            room.ended_at = datetime.utcnow()
            db.session.commit()
            
            # 計算最終排名
            rankings = get_room_rankings(room_id)
            
            socketio.emit('game_finished', {
                'rankings': rankings
            }, room=room_id)
            
            return jsonify({
                'message': '遊戲結束',
                'rankings': rankings
            }), 200
        else:
            # 下一回合
            room.current_round += 1
            db.session.commit()
            
            socketio.emit('next_round', {
                'current_round': room.current_round,
                'total_rounds': room.total_rounds
            }, room=room_id)
            
            return jsonify({
                'message': '進入下一回合',
                'current_round': room.current_round
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '進入下一回合失敗'}), 500

@game_bp.route('/<room_id>/rankings', methods=['GET'])
def get_rankings(room_id):
    """取得房間排名"""
    try:
        room = GameRoom.query.get(room_id)
        if not room:
            return jsonify({'error': '房間不存在'}), 404
        
        rankings = get_room_rankings(room_id)
        
        return jsonify({
            'rankings': rankings
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得排名失敗'}), 500

def get_room_rankings(room_id: str) -> list:
    """取得房間排名（內部函式）"""
    sessions = GameSession.query.filter_by(room_id=room_id).all()
    rankings = []
    
    for session in sessions:
        user = User.query.get(session.user_id)
        if user:
            ranking_info = session.to_dict()
            ranking_info['username'] = user.username
            rankings.append(ranking_info)
    
    # 按分數排序
    rankings.sort(key=lambda x: (x['score'], -x['time_taken']), reverse=True)
    
    # 添加排名
    for i, ranking in enumerate(rankings):
        ranking['rank'] = i + 1
    
    return rankings 