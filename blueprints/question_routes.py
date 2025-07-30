from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Question, User
from marshmallow import Schema, fields, ValidationError
import random

question_bp = Blueprint('questions', __name__)

class QuestionSchema(Schema):
    """題目驗證 Schema"""
    category_id = fields.Str(required=True)
    difficulty = fields.Str(required=True, validate=lambda x: x in ['easy', 'medium', 'hard'])
    question_type = fields.Str(required=True, validate=lambda x: x in ['multiple_choice', 'multi_blank'])
    question_text = fields.Str(required=True)
    options = fields.List(fields.Str(), required=True)
    answer = fields.Raw(required=True)  # 可以是字串或列表
    explanation = fields.Str(required=False)

@question_bp.route('/', methods=['GET'])
def get_questions():
    """取得題目列表"""
    try:
        # 取得查詢參數
        categories = request.args.get('categories', '').split(',') if request.args.get('categories') else []
        difficulties = request.args.get('difficulties', '').split(',') if request.args.get('difficulties') else []
        question_types = request.args.get('types', '').split(',') if request.args.get('types') else []
        limit = request.args.get('limit', type=int, default=10)
        shuffle = request.args.get('shuffle', type=bool, default=False)
        
        # 建立查詢
        query = Question.query
        
        # 套用篩選條件
        if categories and categories[0]:
            # 根據分類名稱找到對應的 category_id
            from models import Category
            category_ids = []
            for cat_name in categories:
                category = Category.query.filter_by(display_name=cat_name).first()
                if category:
                    category_ids.append(category.id)
            
            if category_ids:
                query = query.filter(Question.category_id.in_(category_ids))
        
        if difficulties and difficulties[0]:
            query = query.filter(Question.difficulty.in_(difficulties))
        
        if question_types and question_types[0]:
            query = query.filter(Question.question_type.in_(question_types))
        
        # 隨機排序
        if shuffle:
            query = query.order_by(db.func.random())
        else:
            query = query.order_by(Question.created_at.desc())
        
        # 限制數量
        questions = query.limit(limit).all()
        
        return jsonify({
            'questions': [q.to_dict() for q in questions],
            'total': len(questions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得題目失敗'}), 500

@question_bp.route('/<question_id>', methods=['GET'])
def get_question(question_id):
    """取得指定題目"""
    try:
        question = Question.query.get(question_id)
        
        if not question:
            return jsonify({'error': '題目不存在'}), 404
        
        return jsonify({
            'question': question.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得題目失敗'}), 500

@question_bp.route('/', methods=['POST'])
@jwt_required()
def create_question():
    """建立新題目（管理用途）"""
    try:
        schema = QuestionSchema()
        data = schema.load(request.get_json())
        
        # 驗證答案格式
        if data['question_type'] == 'multiple_choice':
            if not isinstance(data['answer'], str) or data['answer'] not in data['options']:
                return jsonify({'error': '單選題答案必須是選項之一'}), 400
        elif data['question_type'] == 'multi_blank':
            if not isinstance(data['answer'], list):
                return jsonify({'error': '多選題答案必須是列表'}), 400
            if not all(ans in data['options'] for ans in data['answer']):
                return jsonify({'error': '多選題答案必須都是選項之一'}), 400
        
        # 建立新題目
        question = Question(**data)
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'message': '題目建立成功',
            'question': question.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': '驗證錯誤', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '建立題目失敗'}), 500

@question_bp.route('/categories', methods=['GET'])
def get_categories():
    """取得所有題目分類"""
    try:
        # 從 Category 表格取得所有分類
        from models import Category
        categories = Category.query.all()
        return jsonify({
            'categories': [cat.display_name for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得分類失敗'}), 500

@question_bp.route('/difficulties', methods=['GET'])
def get_difficulties():
    """取得所有難度等級"""
    try:
        difficulties = db.session.query(Question.difficulty).distinct().all()
        return jsonify({
            'difficulties': [diff[0] for diff in difficulties]
        }), 200
        
    except Exception as e:
        return jsonify({'error': '取得難度等級失敗'}), 500 