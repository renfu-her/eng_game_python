#!/usr/bin/env python3
"""
遊戲流程測試腳本
測試登入、註冊、房間創建、遊戲開始等功能
"""

import requests
import json
import time

class GameFlowTester:
    def __init__(self):
        self.base_url = 'http://localhost:5000/api'
        self.token = None
        self.user_id = None
        self.room_id = None
        
    def test_register(self):
        """測試註冊功能"""
        print("🔄 測試註冊功能...")
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'test123'
        }
        
        response = requests.post(f'{self.base_url}/auth/register', json=data)
        
        if response.status_code == 201:
            print("✅ 註冊成功")
            return True
        elif response.status_code == 400 and '已存在' in response.text:
            print("ℹ️  使用者已存在，繼續測試")
            return True
        else:
            print(f"❌ 註冊失敗: {response.status_code} - {response.text}")
            return False
    
    def test_login(self):
        """測試登入功能"""
        print("🔄 測試登入功能...")
        
        data = {
            'username': 'testuser',
            'password': 'test123'
        }
        
        response = requests.post(f'{self.base_url}/auth/login', json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.token = result['access_token']
            self.user_id = result['user']['id']
            print("✅ 登入成功")
            return True
        else:
            print(f"❌ 登入失敗: {response.status_code} - {response.text}")
            return False
    
    def test_create_room(self):
        """測試創建房間"""
        print("🔄 測試創建房間...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        data = {
            'name': '測試房間',
            'max_players': 4,
            'total_rounds': 5,
            'categories': ['daily_conversation', 'business_english']
        }
        
        response = requests.post(f'{self.base_url}/rooms/', json=data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            self.room_id = result['room']['id']
            print("✅ 房間創建成功")
            return True
        else:
            print(f"❌ 房間創建失敗: {response.status_code} - {response.text}")
            return False
    
    def test_get_rooms(self):
        """測試取得房間列表"""
        print("🔄 測試取得房間列表...")
        
        response = requests.get(f'{self.base_url}/rooms/')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 取得房間列表成功，共 {result['total']} 個房間")
            return True
        else:
            print(f"❌ 取得房間列表失敗: {response.status_code} - {response.text}")
            return False
    
    def test_get_questions(self):
        """測試取得題目"""
        print("🔄 測試取得題目...")
        
        response = requests.get(f'{self.base_url}/questions/')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 取得題目成功，共 {len(result['questions'])} 題")
            return True
        else:
            print(f"❌ 取得題目失敗: {response.status_code} - {response.text}")
            return False
    
    def test_get_categories(self):
        """測試取得分類"""
        print("🔄 測試取得分類...")
        
        response = requests.get(f'{self.base_url}/questions/categories')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 取得分類成功，共 {len(result['categories'])} 個分類")
            return True
        else:
            print(f"❌ 取得分類失敗: {response.status_code} - {response.text}")
            return False
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 開始執行遊戲流程測試...")
        print("=" * 50)
        
        tests = [
            self.test_register,
            self.test_login,
            self.test_get_categories,
            self.test_get_questions,
            self.test_get_rooms,
            self.test_create_room
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print("-" * 30)
            except Exception as e:
                print(f"❌ 測試執行錯誤: {e}")
                print("-" * 30)
        
        print("=" * 50)
        print(f"🎉 測試完成！通過 {passed}/{total} 個測試")
        
        if passed == total:
            print("✅ 所有功能正常！")
        else:
            print("⚠️  部分功能有問題，請檢查錯誤訊息")

if __name__ == '__main__':
    tester = GameFlowTester()
    tester.run_all_tests() 