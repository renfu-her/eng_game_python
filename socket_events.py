from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from models import User, GameRoom, GameSession
from flask_jwt_extended import decode_token

@socketio.on('connect')
def handle_connect():
    """處理連線事件"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """處理斷線事件"""
    print('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    """處理加入房間事件"""
    try:
        room_id = data.get('room_id')
        token = data.get('token')
        
        if not room_id or not token:
            emit('error', {'message': '缺少必要參數'})
            return
        
        # 驗證 JWT token
        try:
            payload = decode_token(token)
            user_id = payload['sub']
        except:
            emit('error', {'message': '無效的 token'})
            return
        
        # 檢查房間是否存在
        room = GameRoom.query.get(room_id)
        if not room:
            emit('error', {'message': '房間不存在'})
            return
        
        # 檢查使用者是否在房間中
        session = GameSession.query.filter_by(
            user_id=user_id, 
            room_id=room_id
        ).first()
        
        if not session:
            emit('error', {'message': '不在房間中'})
            return
        
        # 加入 Socket.IO 房間
        join_room(room_id)
        
        # 通知其他玩家
        user = User.query.get(user_id)
        emit('player_joined_socket', {
            'user_id': user_id,
            'username': user.username
        }, room=room_id, include_self=False)
        
        print(f'User {user.username} joined room {room_id}')
        
    except Exception as e:
        emit('error', {'message': '加入房間失敗'})
        print(f'Error joining room: {e}')

@socketio.on('leave_room')
def handle_leave_room(data):
    """處理離開房間事件"""
    try:
        room_id = data.get('room_id')
        token = data.get('token')
        
        if not room_id or not token:
            emit('error', {'message': '缺少必要參數'})
            return
        
        # 驗證 JWT token
        try:
            payload = decode_token(token)
            user_id = payload['sub']
        except:
            emit('error', {'message': '無效的 token'})
            return
        
        # 離開 Socket.IO 房間
        leave_room(room_id)
        
        # 通知其他玩家
        user = User.query.get(user_id)
        emit('player_left_socket', {
            'user_id': user_id,
            'username': user.username
        }, room=room_id, include_self=False)
        
        print(f'User {user.username} left room {room_id}')
        
    except Exception as e:
        emit('error', {'message': '離開房間失敗'})
        print(f'Error leaving room: {e}')

@socketio.on('submit_answer_socket')
def handle_submit_answer(data):
    """處理答案提交事件（WebSocket 版本）"""
    try:
        room_id = data.get('room_id')
        token = data.get('token')
        answer = data.get('answer')
        time_taken = data.get('time_taken')
        
        if not all([room_id, token, answer, time_taken is not None]):
            emit('error', {'message': '缺少必要參數'})
            return
        
        # 驗證 JWT token
        try:
            payload = decode_token(token)
            user_id = payload['sub']
        except:
            emit('error', {'message': '無效的 token'})
            return
        
        # 這裡可以添加答案驗證邏輯
        # 為了簡化，我們只發送通知給其他玩家
        
        user = User.query.get(user_id)
        emit('answer_submitted_socket', {
            'user_id': user_id,
            'username': user.username,
            'time_taken': time_taken
        }, room=room_id, include_self=False)
        
        print(f'User {user.username} submitted answer in room {room_id}')
        
    except Exception as e:
        emit('error', {'message': '提交答案失敗'})
        print(f'Error submitting answer: {e}')

@socketio.on('ready_for_next')
def handle_ready_for_next(data):
    """處理準備下一題事件"""
    try:
        room_id = data.get('room_id')
        token = data.get('token')
        
        if not room_id or not token:
            emit('error', {'message': '缺少必要參數'})
            return
        
        # 驗證 JWT token
        try:
            payload = decode_token(token)
            user_id = payload['sub']
        except:
            emit('error', {'message': '無效的 token'})
            return
        
        user = User.query.get(user_id)
        emit('player_ready', {
            'user_id': user_id,
            'username': user.username
        }, room=room_id, include_self=False)
        
        print(f'User {user.username} is ready for next question in room {room_id}')
        
    except Exception as e:
        emit('error', {'message': '準備下一題失敗'})
        print(f'Error ready for next: {e}') 