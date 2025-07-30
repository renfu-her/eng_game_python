from app import create_app, db
from models import User, Question
from werkzeug.security import generate_password_hash

def init_database():
    """初始化資料庫"""
    app = create_app()
    
    with app.app_context():
        # 建立所有表格
        db.create_all()
        
        # 建立管理員帳號
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print('管理員帳號建立成功')
        
        # 建立範例題目
        if Question.query.count() == 0:
            sample_questions = [
                # 日常生活 - 單選題
                {
                    'category': '日常生活（Daily Conversation）',
                    'difficulty': 'easy',
                    'question_type': 'multiple_choice',
                    'question_text': 'I ___ to the gym every morning.',
                    'options': ['go', 'going', 'gone', 'goes'],
                    'answer': 'go',
                    'explanation': '使用現在簡單式表示習慣性動作'
                },
                {
                    'category': '日常生活（Daily Conversation）',
                    'difficulty': 'easy',
                    'question_type': 'multiple_choice',
                    'question_text': 'What time do you usually ___ up?',
                    'options': ['wake', 'waking', 'wakes', 'woken'],
                    'answer': 'wake',
                    'explanation': '使用動詞原形'
                },
                {
                    'category': '日常生活（Daily Conversation）',
                    'difficulty': 'medium',
                    'question_type': 'multiple_choice',
                    'question_text': 'She ___ her homework before dinner.',
                    'options': ['finishes', 'finish', 'finishing', 'finished'],
                    'answer': 'finishes',
                    'explanation': '第三人稱單數現在簡單式'
                },
                
                # 旅遊與交通 - 單選題
                {
                    'category': '旅遊與交通（Travel & Transport）',
                    'difficulty': 'easy',
                    'question_type': 'multiple_choice',
                    'question_text': 'How do you ___ to work?',
                    'options': ['get', 'getting', 'gets', 'got'],
                    'answer': 'get',
                    'explanation': '使用動詞原形'
                },
                {
                    'category': '旅遊與交通（Travel & Transport）',
                    'difficulty': 'medium',
                    'question_type': 'multiple_choice',
                    'question_text': 'The train ___ at 3 PM.',
                    'options': ['arrives', 'arrive', 'arriving', 'arrived'],
                    'answer': 'arrives',
                    'explanation': '第三人稱單數現在簡單式'
                },
                
                # 商業英語 - 單選題
                {
                    'category': '商業英語（Business English）',
                    'difficulty': 'medium',
                    'question_type': 'multiple_choice',
                    'question_text': 'We ___ the meeting tomorrow.',
                    'options': ['will have', 'have', 'having', 'had'],
                    'answer': 'will have',
                    'explanation': '使用未來式表示計劃'
                },
                {
                    'category': '商業英語（Business English）',
                    'difficulty': 'hard',
                    'question_type': 'multiple_choice',
                    'question_text': 'The project ___ by next month.',
                    'options': ['will be completed', 'completes', 'completing', 'completed'],
                    'answer': 'will be completed',
                    'explanation': '使用未來被動式'
                },
                
                # 校園生活 - 單選題
                {
                    'category': '校園生活（Campus Life）',
                    'difficulty': 'easy',
                    'question_type': 'multiple_choice',
                    'question_text': 'What subjects do you ___?',
                    'options': ['study', 'studying', 'studies', 'studied'],
                    'answer': 'study',
                    'explanation': '使用動詞原形'
                },
                {
                    'category': '校園生活（Campus Life）',
                    'difficulty': 'medium',
                    'question_type': 'multiple_choice',
                    'question_text': 'The library ___ at 10 PM.',
                    'options': ['closes', 'close', 'closing', 'closed'],
                    'answer': 'closes',
                    'explanation': '第三人稱單數現在簡單式'
                },
                
                # 健康與醫療 - 單選題
                {
                    'category': '健康與醫療（Health & Medical）',
                    'difficulty': 'medium',
                    'question_type': 'multiple_choice',
                    'question_text': 'You should ___ more water.',
                    'options': ['drink', 'drinking', 'drinks', 'drank'],
                    'answer': 'drink',
                    'explanation': '使用動詞原形'
                },
                {
                    'category': '健康與醫療（Health & Medical）',
                    'difficulty': 'hard',
                    'question_type': 'multiple_choice',
                    'question_text': 'The doctor ___ the patient carefully.',
                    'options': ['examines', 'examine', 'examining', 'examined'],
                    'answer': 'examines',
                    'explanation': '第三人稱單數現在簡單式'
                },
                
                # 多重填空題
                {
                    'category': '日常生活（Daily Conversation）',
                    'difficulty': 'medium',
                    'question_type': 'multi_blank',
                    'question_text': 'I usually ___ up at 7 AM, then I ___ breakfast and ___ to work.',
                    'options': ['go', 'eat', 'wake', 'drink', 'run'],
                    'answer': ['wake', 'eat', 'go'],
                    'explanation': '按照時間順序填入動詞'
                },
                {
                    'category': '旅遊與交通（Travel & Transport）',
                    'difficulty': 'medium',
                    'question_type': 'multi_blank',
                    'question_text': 'First, I ___ my ticket, then I ___ the platform and ___ the train.',
                    'options': ['buy', 'board', 'find', 'check', 'wait'],
                    'answer': ['buy', 'find', 'board'],
                    'explanation': '按照旅行流程填入動詞'
                },
                {
                    'category': '商業英語（Business English）',
                    'difficulty': 'hard',
                    'question_type': 'multi_blank',
                    'question_text': 'We ___ the proposal, ___ the budget, and ___ the project.',
                    'options': ['approve', 'review', 'start', 'finish', 'discuss'],
                    'answer': ['review', 'approve', 'start'],
                    'explanation': '按照商業流程填入動詞'
                },
                {
                    'category': '校園生活（Campus Life）',
                    'difficulty': 'medium',
                    'question_type': 'multi_blank',
                    'question_text': 'Students ___ the classroom, ___ their books, and ___ to the teacher.',
                    'options': ['enter', 'open', 'listen', 'write', 'read'],
                    'answer': ['enter', 'open', 'listen'],
                    'explanation': '按照上課流程填入動詞'
                },
                {
                    'category': '健康與醫療（Health & Medical）',
                    'difficulty': 'hard',
                    'question_type': 'multi_blank',
                    'question_text': 'The nurse ___ the patient, ___ the temperature, and ___ the doctor.',
                    'options': ['calls', 'checks', 'takes', 'gives', 'helps'],
                    'answer': ['checks', 'takes', 'calls'],
                    'explanation': '按照醫療流程填入動詞'
                }
            ]
            
            for q_data in sample_questions:
                question = Question(**q_data)
                db.session.add(question)
            
            print(f'{len(sample_questions)} 個範例題目建立成功')
        
        db.session.commit()
        print('資料庫初始化完成！')

if __name__ == '__main__':
    init_database() 