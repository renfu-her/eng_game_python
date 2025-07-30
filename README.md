# 🎮 英文對答遊戲

一個基於 Flask 的多人即時英文學習遊戲，支援多種題型與即時互動。

## 🚀 功能特色

- **多種題型**：單選題、多重填空題
- **題目分類**：日常生活、旅遊交通、商業英語、校園生活、健康醫療
- **多人遊戲**：即時多人對答，支援房間系統
- **即時互動**：WebSocket 即時通訊
- **排名系統**：即時排行榜與成績統計
- **JWT 認證**：安全的用戶認證系統

## 📋 系統需求

- Python 3.8+
- MySQL 5.7+
- Git

## 🛠️ 安裝步驟

### 1. 克隆專案
```bash
git clone <repository-url>
cd eng-game
```

### 2. 建立虛擬環境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 設定資料庫
```sql
CREATE DATABASE eng_game_python CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 初始化資料庫
```bash
python init_db.py
```

### 6. 啟動應用程式
```bash
python app.py
```

應用程式將在 `http://localhost:5000` 啟動

## 📚 API 文件

### 認證 API

#### 註冊
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

#### 登入
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

### 題目 API

#### 取得題目列表
```http
GET /api/questions?categories=daily,travel&difficulties=easy,medium&limit=10&shuffle=true
```

#### 取得題目分類
```http
GET /api/questions/categories
```

### 房間 API

#### 建立房間
```http
POST /api/rooms
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "測試房間",
  "max_players": 5,
  "total_rounds": 10,
  "categories": ["日常生活（Daily Conversation）", "旅遊與交通（Travel & Transport）"]
}
```

#### 加入房間
```http
POST /api/rooms/<room_id>/join
Authorization: Bearer <token>
```

#### 開始遊戲
```http
POST /api/rooms/<room_id>/start
Authorization: Bearer <token>
```

### 遊戲 API

#### 取得當前題目
```http
GET /api/game/<room_id>/current-question
Authorization: Bearer <token>
```

#### 提交答案
```http
POST /api/game/<room_id>/submit-answer
Authorization: Bearer <token>
Content-Type: application/json

{
  "answer": "go",
  "time_taken": 15.5
}
```

#### 進入下一回合
```http
POST /api/game/<room_id>/next-round
Authorization: Bearer <token>
```

## 🔌 WebSocket 事件

### 客戶端事件
- `join_room`: 加入房間
- `leave_room`: 離開房間
- `submit_answer_socket`: 提交答案
- `ready_for_next`: 準備下一題

### 伺服器事件
- `player_joined_socket`: 玩家加入
- `player_left_socket`: 玩家離開
- `game_started`: 遊戲開始
- `next_round`: 下一回合
- `answer_submitted_socket`: 答案提交
- `player_ready`: 玩家準備
- `game_finished`: 遊戲結束

## 🗄️ 資料庫結構

### 主要表格
- `users`: 使用者資訊
- `questions`: 題目資料
- `game_rooms`: 遊戲房間
- `game_sessions`: 遊戲會話
- `room_questions`: 房間題目關聯
- `player_answers`: 玩家答案

## 🎯 遊戲流程

1. **註冊/登入**：使用者建立帳號或登入
2. **建立/加入房間**：選擇題目分類與遊戲設定
3. **等待玩家**：房主等待其他玩家加入
4. **開始遊戲**：房主開始遊戲，系統隨機選擇題目
5. **答題階段**：玩家在時限內答題
6. **結果顯示**：顯示答案與解釋
7. **下一回合**：進入下一題或結束遊戲
8. **最終排名**：顯示遊戲結果與排名

## 🔧 開發指南

### 專案結構
```
eng-game/
├── app.py                 # 主應用程式
├── config.py             # 設定檔
├── models.py             # 資料模型
├── socket_events.py      # WebSocket 事件
├── init_db.py           # 資料庫初始化
├── requirements.txt     # 依賴套件
├── README.md           # 說明文件
└── blueprints/         # 藍圖模組
    ├── __init__.py
    ├── auth_routes.py   # 認證路由
    ├── question_routes.py # 題目路由
    ├── room_routes.py   # 房間路由
    └── game_routes.py   # 遊戲路由
```

### 新增題目
```python
from app import create_app, db
from models import Question

app = create_app()
with app.app_context():
    question = Question(
        category='日常生活（Daily Conversation）',
        difficulty='easy',
        question_type='multiple_choice',
        question_text='I ___ to school every day.',
        options=['go', 'going', 'goes', 'went'],
        answer='go',
        explanation='使用現在簡單式表示習慣性動作'
    )
    db.session.add(question)
    db.session.commit()
```

## 🚀 部署

### 生產環境設定
1. 設定環境變數
2. 使用 Gunicorn 部署
3. 設定 Nginx 反向代理
4. 配置 SSL 憑證

```bash
# 使用 Gunicorn 啟動
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## 📝 授權

本專案採用 MIT 授權條款。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📞 聯絡資訊

如有問題，請透過以下方式聯絡：
- Email: your-email@example.com
- GitHub Issues: [專案 Issues 頁面] # eng_game_python
