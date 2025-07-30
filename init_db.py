from app import create_app, db
from models import User, Question, Category
from werkzeug.security import generate_password_hash
import json

def init_database():
    """初始化資料庫"""
    app = create_app()
    
    with app.app_context():
        try:
            # 建立所有表格
            db.create_all()
            print('✅ 資料庫表格建立成功')
            
            # 建立管理員帳號
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@example.com'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                print('✅ 管理員帳號建立成功')
            else:
                print('ℹ️  管理員帳號已存在')
            
            # 建立題目分類
            categories_data = [
                {
                    'name': 'daily_conversation',
                    'display_name': '日常生活（Daily Conversation）',
                    'description': '日常生活中的常用英語對話和表達'
                },
                {
                    'name': 'travel_transport',
                    'display_name': '旅遊與交通（Travel & Transport）',
                    'description': '旅遊和交通相關的英語詞彙和表達'
                },
                {
                    'name': 'business_english',
                    'display_name': '商業英語（Business English）',
                    'description': '商業場合和職場中使用的英語'
                },
                {
                    'name': 'campus_life',
                    'display_name': '校園生活（Campus Life）',
                    'description': '學校和校園生活中的英語表達'
                },
                {
                    'name': 'health_medical',
                    'display_name': '健康與醫療（Health & Medical）',
                    'description': '健康和醫療相關的英語詞彙'
                }
            ]
            
            # 建立或更新分類
            categories = {}
            for cat_data in categories_data:
                category = Category.query.filter_by(name=cat_data['name']).first()
                if not category:
                    category = Category(**cat_data)
                    db.session.add(category)
                    print(f'✅ 分類建立成功: {cat_data["display_name"]}')
                else:
                    print(f'ℹ️  分類已存在: {cat_data["display_name"]}')
                categories[cat_data['name']] = category
            
            db.session.commit()  # 先提交分類，確保有 ID
            
            # 建立範例題目
            if Question.query.count() == 0:
                sample_questions = [
                    # 日常生活 - 單選題
                    {
                        'category_id': categories['daily_conversation'].id,
                        'difficulty': 'easy',
                        'question_type': 'multiple_choice',
                        'question_text': 'I ___ to the gym every morning.',
                        'options': json.dumps(['go', 'going', 'gone', 'goes']),
                        'answer': 'go',
                        'explanation': '使用現在簡單式表示習慣性動作'
                    },
                    {
                        'category_id': categories['daily_conversation'].id,
                        'difficulty': 'easy',
                        'question_type': 'multiple_choice',
                        'question_text': 'What time do you usually ___ up?',
                        'options': json.dumps(['wake', 'waking', 'wakes', 'woken']),
                        'answer': 'wake',
                        'explanation': '使用動詞原形'
                    },
                    {
                        'category_id': categories['daily_conversation'].id,
                        'difficulty': 'medium',
                        'question_type': 'multiple_choice',
                        'question_text': 'She ___ her homework before dinner.',
                        'options': json.dumps(['finishes', 'finish', 'finishing', 'finished']),
                        'answer': 'finishes',
                        'explanation': '第三人稱單數現在簡單式'
                    },
                    
                    # 旅遊與交通 - 單選題
                    {
                        'category_id': categories['travel_transport'].id,
                        'difficulty': 'easy',
                        'question_type': 'multiple_choice',
                        'question_text': 'How do you ___ to work?',
                        'options': json.dumps(['get', 'getting', 'gets', 'got']),
                        'answer': 'get',
                        'explanation': '使用動詞原形'
                    },
                    {
                        'category_id': categories['travel_transport'].id,
                        'difficulty': 'medium',
                        'question_type': 'multiple_choice',
                        'question_text': 'The train ___ at 3 PM.',
                        'options': json.dumps(['arrives', 'arrive', 'arriving', 'arrived']),
                        'answer': 'arrives',
                        'explanation': '第三人稱單數現在簡單式'
                    },
                    
                    # 商業英語 - 單選題
                    {
                        'category_id': categories['business_english'].id,
                        'difficulty': 'medium',
                        'question_type': 'multiple_choice',
                        'question_text': 'We ___ the meeting tomorrow.',
                        'options': json.dumps(['will have', 'have', 'having', 'had']),
                        'answer': 'will have',
                        'explanation': '使用未來式表示計劃'
                    },
                    {
                        'category_id': categories['business_english'].id,
                        'difficulty': 'hard',
                        'question_type': 'multiple_choice',
                        'question_text': 'The project ___ by next month.',
                        'options': json.dumps(['will be completed', 'completes', 'completing', 'completed']),
                        'answer': 'will be completed',
                        'explanation': '使用未來被動式'
                    },
                    
                    # 校園生活 - 單選題
                    {
                        'category_id': categories['campus_life'].id,
                        'difficulty': 'easy',
                        'question_type': 'multiple_choice',
                        'question_text': 'What subjects do you ___?',
                        'options': json.dumps(['study', 'studying', 'studies', 'studied']),
                        'answer': 'study',
                        'explanation': '使用動詞原形'
                    },
                    {
                        'category_id': categories['campus_life'].id,
                        'difficulty': 'medium',
                        'question_type': 'multiple_choice',
                        'question_text': 'The library ___ at 10 PM.',
                        'options': json.dumps(['closes', 'close', 'closing', 'closed']),
                        'answer': 'closes',
                        'explanation': '第三人稱單數現在簡單式'
                    },
                    
                    # 健康與醫療 - 單選題
                    {
                        'category_id': categories['health_medical'].id,
                        'difficulty': 'medium',
                        'question_type': 'multiple_choice',
                        'question_text': 'You should ___ more water.',
                        'options': json.dumps(['drink', 'drinking', 'drinks', 'drank']),
                        'answer': 'drink',
                        'explanation': '使用動詞原形'
                    },
                    {
                        'category_id': categories['health_medical'].id,
                        'difficulty': 'hard',
                        'question_type': 'multiple_choice',
                        'question_text': 'The doctor ___ the patient carefully.',
                        'options': json.dumps(['examines', 'examine', 'examining', 'examined']),
                        'answer': 'examines',
                        'explanation': '第三人稱單數現在簡單式'
                    },
                    
                    # 多重填空題
                    {
                        'category_id': categories['daily_conversation'].id,
                        'difficulty': 'medium',
                        'question_type': 'multi_blank',
                        'question_text': 'I usually ___ up at 7 AM, then I ___ breakfast and ___ to work.',
                        'options': json.dumps(['go', 'eat', 'wake', 'drink', 'run']),
                        'answer': json.dumps(['wake', 'eat', 'go']),
                        'explanation': '按照時間順序填入動詞'
                    },
                    {
                        'category_id': categories['travel_transport'].id,
                        'difficulty': 'medium',
                        'question_type': 'multi_blank',
                        'question_text': 'First, I ___ my ticket, then I ___ the platform and ___ the train.',
                        'options': json.dumps(['buy', 'board', 'find', 'check', 'wait']),
                        'answer': json.dumps(['buy', 'find', 'board']),
                        'explanation': '按照旅行流程填入動詞'
                    },
                    {
                        'category_id': categories['business_english'].id,
                        'difficulty': 'hard',
                        'question_type': 'multi_blank',
                        'question_text': 'We ___ the proposal, ___ the budget, and ___ the project.',
                        'options': json.dumps(['approve', 'review', 'start', 'finish', 'discuss']),
                        'answer': json.dumps(['review', 'approve', 'start']),
                        'explanation': '按照商業流程填入動詞'
                    },
                    {
                        'category_id': categories['campus_life'].id,
                        'difficulty': 'medium',
                        'question_type': 'multi_blank',
                        'question_text': 'Students ___ the classroom, ___ their books, and ___ to the teacher.',
                        'options': json.dumps(['enter', 'open', 'listen', 'write', 'read']),
                        'answer': json.dumps(['enter', 'open', 'listen']),
                        'explanation': '按照上課流程填入動詞'
                    },
                    {
                        'category_id': categories['health_medical'].id,
                        'difficulty': 'hard',
                        'question_type': 'multi_blank',
                        'question_text': 'The nurse ___ the patient, ___ the temperature, and ___ the doctor.',
                        'options': json.dumps(['calls', 'checks', 'takes', 'gives', 'helps']),
                        'answer': json.dumps(['checks', 'takes', 'calls']),
                        'explanation': '按照醫療流程填入動詞'
                    }
                ]
                
                for q_data in sample_questions:
                    question = Question(**q_data)
                    db.session.add(question)
                
                print(f'✅ {len(sample_questions)} 個範例題目建立成功')
            else:
                print('ℹ️  範例題目已存在')
            
            db.session.commit()
            print('🎉 資料庫初始化完成！')
            print('📊 統計資訊：')
            print(f'   - 使用者數量: {User.query.count()}')
            print(f'   - 分類數量: {Category.query.count()}')
            print(f'   - 題目數量: {Question.query.count()}')
            
        except Exception as e:
            db.session.rollback()
            print(f'❌ 資料庫初始化失敗: {e}')
            raise

if __name__ == '__main__':
    init_database() 