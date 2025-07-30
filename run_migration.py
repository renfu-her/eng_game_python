#!/usr/bin/env python3
"""
資料庫遷移執行腳本
執行順序：
1. 執行 SQL 遷移腳本
2. 執行 Python 遷移腳本
3. 重新初始化資料庫（如果需要）
"""

import subprocess
import sys
import os
from app import create_app, db
from models import User, Question, Category

def run_sql_migration():
    """執行 SQL 遷移腳本"""
    print('🔄 執行 SQL 遷移腳本...')
    
    # 讀取 SQL 腳本
    with open('database_migration.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # 這裡需要根據您的資料庫設定來執行 SQL
    # 如果您使用 MySQL，可以使用以下方式：
    try:
        # 使用 mysql 命令列工具執行
        result = subprocess.run([
            'mysql', '-u', 'root', '-h', '127.0.0.1', 'eng_game_python'
        ], input=sql_script, text=True, capture_output=True)
        
        if result.returncode == 0:
            print('✅ SQL 遷移執行成功')
        else:
            print(f'❌ SQL 遷移失敗: {result.stderr}')
            return False
            
    except FileNotFoundError:
        print('⚠️  mysql 命令列工具未找到，請手動執行 database_migration.sql')
        print('   或者確保 MySQL 客戶端已安裝並在 PATH 中')
        return False
    
    return True

def run_python_migration():
    """執行 Python 遷移腳本"""
    print('🔄 執行 Python 遷移腳本...')
    
    try:
        result = subprocess.run([sys.executable, 'migrate_categories.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print('✅ Python 遷移執行成功')
            print(result.stdout)
        else:
            print(f'❌ Python 遷移失敗: {result.stderr}')
            return False
            
    except Exception as e:
        print(f'❌ 執行 Python 遷移時發生錯誤: {e}')
        return False
    
    return True

def verify_migration():
    """驗證遷移結果"""
    print('🔄 驗證遷移結果...')
    
    app = create_app()
    with app.app_context():
        try:
            category_count = Category.query.count()
            question_count = Question.query.count()
            
            print(f'✅ 驗證完成:')
            print(f'   - 分類數量: {category_count}')
            print(f'   - 題目數量: {question_count}')
            
            # 檢查是否有題目沒有分類
            questions_without_category = Question.query.filter_by(category_id=None).count()
            if questions_without_category > 0:
                print(f'⚠️  有 {questions_without_category} 個題目沒有分類')
            else:
                print('✅ 所有題目都有正確的分類關聯')
                
            return True
            
        except Exception as e:
            print(f'❌ 驗證失敗: {e}')
            return False

def main():
    """主函式"""
    print('🚀 開始執行資料庫遷移...')
    print('=' * 50)
    
    # 1. 執行 SQL 遷移
    if not run_sql_migration():
        print('❌ SQL 遷移失敗，停止執行')
        return
    
    print('-' * 50)
    
    # 2. 執行 Python 遷移
    if not run_python_migration():
        print('❌ Python 遷移失敗，停止執行')
        return
    
    print('-' * 50)
    
    # 3. 驗證遷移結果
    if not verify_migration():
        print('❌ 遷移驗證失敗')
        return
    
    print('=' * 50)
    print('🎉 資料庫遷移完成！')
    print('\n📝 注意事項:')
    print('1. 舊的 category 欄位仍然保留，建議在確認一切正常後手動移除')
    print('2. 如果遇到問題，可以檢查 migrate_categories.py 的輸出')
    print('3. 建議備份資料庫後再執行此遷移')

if __name__ == '__main__':
    main() 