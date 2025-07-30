from app import create_app, db
from models import User, Question, Category
from sqlalchemy import text
import json

def migrate_categories():
    """遷移分類資料到新的 categories 表格"""
    app = create_app()
    
    with app.app_context():
        try:
            print('🔄 開始遷移分類資料...')
            
            # 檢查是否已經有 categories 表格
            if Category.query.count() > 0:
                print('ℹ️  categories 表格已存在，繼續處理資料關聯...')
            
            # 從現有的 questions 表格中提取唯一的分類
            result = db.session.execute(text('SELECT DISTINCT category FROM questions WHERE category IS NOT NULL'))
            existing_categories = [row[0] for row in result]
            category_mapping = {}
            
            # 建立分類對應表
            category_data = {
                '日常生活（Daily Conversation）': {
                    'name': 'daily_conversation',
                    'display_name': '日常生活（Daily Conversation）',
                    'description': '日常生活中的常用英語對話和表達'
                },
                '旅遊與交通（Travel & Transport）': {
                    'name': 'travel_transport',
                    'display_name': '旅遊與交通（Travel & Transport）',
                    'description': '旅遊和交通相關的英語詞彙和表達'
                },
                '商業英語（Business English）': {
                    'name': 'business_english',
                    'display_name': '商業英語（Business English）',
                    'description': '商業場合和職場中使用的英語'
                },
                '校園生活（Campus Life）': {
                    'name': 'campus_life',
                    'display_name': '校園生活（Campus Life）',
                    'description': '學校和校園生活中的英語表達'
                },
                '健康與醫療（Health & Medical）': {
                    'name': 'health_medical',
                    'display_name': '健康與醫療（Health & Medical）',
                    'description': '健康和醫療相關的英語詞彙'
                }
            }
            
            # 建立新的分類記錄
            for old_category_name in existing_categories:
                if old_category_name in category_data:
                    cat_data = category_data[old_category_name]
                    
                    # 檢查分類是否已存在
                    existing_category = Category.query.filter_by(name=cat_data['name']).first()
                    if existing_category:
                        category = existing_category
                        print(f'ℹ️  分類已存在: {cat_data["display_name"]}')
                    else:
                        category = Category(**cat_data)
                        db.session.add(category)
                        db.session.flush()  # 獲取 ID
                        print(f'✅ 建立分類: {cat_data["display_name"]}')
                    
                    category_mapping[old_category_name] = category.id
                else:
                    print(f'⚠️  未知分類: {old_category_name}')
            
            db.session.commit()
            print(f'✅ 建立了 {len(category_mapping)} 個分類')
            
            # 更新所有題目的 category_id
            questions = Question.query.all()
            updated_count = 0
            
            for question in questions:
                if question.category in category_mapping:
                    question.category_id = category_mapping[question.category]
                    updated_count += 1
                else:
                    print(f'⚠️  題目 {question.id} 的分類 "{question.category}" 無法對應')
            
            db.session.commit()
            print(f'✅ 更新了 {updated_count} 個題目的分類關聯')
            
            print('🎉 分類遷移完成！')
            
        except Exception as e:
            db.session.rollback()
            print(f'❌ 遷移失敗: {e}')
            raise

if __name__ == '__main__':
    migrate_categories() 