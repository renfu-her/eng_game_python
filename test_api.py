#!/usr/bin/env python3
"""
API 測試腳本
用於測試英文遊戲的各項功能
"""

import requests
import json
import time

# 設定
BASE_URL = 'http://localhost:5000/api'
TOKEN = None

def print_response(response, title=""):
    """印出回應"""
    print(f"\n{'='*50}")
    if title:
        print(f"📋 {title}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print(f"{'='*50}")

def test_auth():
    """測試認證功能"""
    global TOKEN
    
    print("🔐 測試認證功能")
    
    # 註冊
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response(response, "註冊")
    
    # 登入
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(response, "登入")
    
    if response.status_code == 200:
        TOKEN = response.json()['access_token']
        print(f"✅ Token: {TOKEN[:20]}...")

def test_questions():
    """測試題目功能"""
    print("\n📝 測試題目功能")
    
    # 取得題目分類
    response = requests.get(f"{BASE_URL}/questions/categories")
    print_response(response, "取得題目分類")
    
    # 取得題目列表
    response = requests.get(f"{BASE_URL}/questions?limit=5&shuffle=true")
    print_response(response, "取得題目列表")
    
    # 取得特定分類題目
    response = requests.get(f"{BASE_URL}/questions?categories=日常生活（Daily Conversation）&limit=3")
    print_response(response, "取得特定分類題目")

def test_rooms():
    """測試房間功能"""
    global TOKEN
    
    if not TOKEN:
        print("❌ 需要先登入")
        return
    
    print("\n🏠 測試房間功能")
    
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    # 建立房間
    room_data = {
        "name": "測試房間",
        "max_players": 5,
        "total_rounds": 5,
        "categories": ["日常生活（Daily Conversation）", "旅遊與交通（Travel & Transport）"]
    }
    
    response = requests.post(f"{BASE_URL}/rooms", json=room_data, headers=headers)
    print_response(response, "建立房間")
    
    if response.status_code == 201:
        room_id = response.json()['room']['id']
        
        # 取得房間資訊
        response = requests.get(f"{BASE_URL}/rooms/{room_id}")
        print_response(response, "取得房間資訊")
        
        # 開始遊戲
        response = requests.post(f"{BASE_URL}/rooms/{room_id}/start", headers=headers)
        print_response(response, "開始遊戲")
        
        return room_id
    
    return None

def test_game(room_id):
    """測試遊戲功能"""
    global TOKEN
    
    if not TOKEN or not room_id:
        print("❌ 需要先登入並建立房間")
        return
    
    print("\n🎮 測試遊戲功能")
    
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    # 取得當前題目
    response = requests.get(f"{BASE_URL}/game/{room_id}/current-question", headers=headers)
    print_response(response, "取得當前題目")
    
    if response.status_code == 200:
        question = response.json()['question']
        
        # 提交答案
        answer_data = {
            "answer": question['answer'],
            "time_taken": 15.5
        }
        
        response = requests.post(f"{BASE_URL}/game/{room_id}/submit-answer", 
                               json=answer_data, headers=headers)
        print_response(response, "提交答案")
        
        # 進入下一回合
        response = requests.post(f"{BASE_URL}/game/{room_id}/next-round", headers=headers)
        print_response(response, "進入下一回合")
        
        # 取得排名
        response = requests.get(f"{BASE_URL}/game/{room_id}/rankings")
        print_response(response, "取得排名")

def main():
    """主測試函式"""
    print("🎯 英文遊戲 API 測試")
    print("請確保應用程式正在運行在 http://localhost:5000")
    
    try:
        # 測試認證
        test_auth()
        
        # 測試題目
        test_questions()
        
        # 測試房間
        room_id = test_rooms()
        
        # 測試遊戲
        if room_id:
            test_game(room_id)
        
        print("\n✅ 所有測試完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到應用程式，請確保應用程式正在運行")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 