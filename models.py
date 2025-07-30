from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    """使用者模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    game_sessions = db.relationship('GameSession', backref='user', lazy=True)
    
    def set_password(self, password: str) -> None:
        """設定密碼"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    """題目分類模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    questions = db.relationship('Question', backref='category', lazy=True)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'question_count': len(self.questions)
        }

class Question(db.Model):
    """題目模型"""
    __tablename__ = 'questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False, index=True)  # easy, medium, hard
    question_type = db.Column(db.String(30), nullable=False)  # multiple_choice, multi_blank
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)  # 選項列表
    answer = db.Column(db.JSON, nullable=False)  # 答案（單選為字串，多選為列表）
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'id': self.id,
            'category': self.category.display_name if self.category else None,
            'category_id': self.category_id,
            'difficulty': self.difficulty,
            'type': self.question_type,
            'question': self.question_text,
            'options': self.options,
            'answer': self.answer,
            'explanation': self.explanation
        }

class GameRoom(db.Model):
    """遊戲房間模型"""
    __tablename__ = 'game_rooms'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, in_progress, finished
    max_players = db.Column(db.Integer, default=10)
    current_round = db.Column(db.Integer, default=0)
    total_rounds = db.Column(db.Integer, default=10)
    categories = db.Column(db.JSON, nullable=False)  # 題目分類列表
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    # 關聯
    players = db.relationship('GameSession', backref='room', lazy=True)
    questions = db.relationship('RoomQuestion', backref='room', lazy=True)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'max_players': self.max_players,
            'current_round': self.current_round,
            'total_rounds': self.total_rounds,
            'categories': self.categories,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'player_count': len(self.players)
        }

class GameSession(db.Model):
    """遊戲會話模型"""
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.String(36), db.ForeignKey('game_rooms.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    total_answers = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime, nullable=True)
    
    # 關聯
    answers = db.relationship('PlayerAnswer', backref='session', lazy=True)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'score': self.score,
            'correct_answers': self.correct_answers,
            'total_answers': self.total_answers,
            'accuracy': round(self.correct_answers / self.total_answers * 100, 2) if self.total_answers > 0 else 0,
            'joined_at': self.joined_at.isoformat(),
            'left_at': self.left_at.isoformat() if self.left_at else None
        }

class RoomQuestion(db.Model):
    """房間題目關聯模型"""
    __tablename__ = 'room_questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = db.Column(db.String(36), db.ForeignKey('game_rooms.id'), nullable=False)
    question_id = db.Column(db.String(36), db.ForeignKey('questions.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    order_in_round = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Integer, default=30)  # 秒數
    
    # 關聯
    question = db.relationship('Question', lazy=True)
    answers = db.relationship('PlayerAnswer', backref='room_question', lazy=True)

class PlayerAnswer(db.Model):
    """玩家答案模型"""
    __tablename__ = 'player_answers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('game_sessions.id'), nullable=False)
    room_question_id = db.Column(db.String(36), db.ForeignKey('room_questions.id'), nullable=False)
    answer = db.Column(db.JSON, nullable=False)  # 玩家的答案
    is_correct = db.Column(db.Boolean, nullable=False)
    time_taken = db.Column(db.Float, nullable=False)  # 答題時間（秒）
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'room_question_id': self.room_question_id,
            'answer': self.answer,
            'is_correct': self.is_correct,
            'time_taken': self.time_taken,
            'answered_at': self.answered_at.isoformat()
        } 