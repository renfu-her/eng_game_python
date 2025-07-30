# 🚀 純 Python 部署指南

## 📋 概述

本專案採用純 Python 技術棧，無需 Docker 容器化，可直接在各種環境中部署運行。

---

## 🛠️ 本地開發環境

### 快速啟動
```bash
# Windows
start.bat

# Linux/macOS
./start.sh
```

### 手動啟動
```bash
# 1. 建立虛擬環境
python -m venv venv

# 2. 啟動虛擬環境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 初始化資料庫
python init_db.py

# 5. 啟動應用程式
python run.py
```

---

## 🏭 生產環境部署

### 1. 使用 Gunicorn (推薦)

#### 安裝 Gunicorn
```bash
pip install gunicorn
```

#### 建立 Gunicorn 配置檔案
```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

#### 啟動命令
```bash
gunicorn -c gunicorn.conf.py "app:create_app()"
```

### 2. 使用 uWSGI

#### 安裝 uWSGI
```bash
pip install uwsgi
```

#### uWSGI 配置檔案
```ini
# uwsgi.ini
[uwsgi]
http = 0.0.0.0:5000
module = app:create_app()
callable = app
master = true
processes = 4
threads = 2
enable-threads = true
buffer-size = 32768
max-requests = 1000
harakiri = 30
```

#### 啟動命令
```bash
uwsgi --ini uwsgi.ini
```

---

## 🌐 反向代理配置

### Nginx 配置

#### 安裝 Nginx
```bash
# Ubuntu/Debian
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### Nginx 配置檔案
```nginx
# /etc/nginx/sites-available/eng-game
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支援
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static/ {
        alias /path/to/your/app/static/;
        expires 30d;
    }
}
```

#### 啟用站點
```bash
sudo ln -s /etc/nginx/sites-available/eng-game /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Apache 配置

#### 安裝 mod_wsgi
```bash
# Ubuntu/Debian
sudo apt-get install libapache2-mod-wsgi-py3

# CentOS/RHEL
sudo yum install mod_wsgi
```

#### Apache 虛擬主機配置
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    
    WSGIDaemonProcess eng-game python-path=/path/to/your/app:/path/to/venv/lib/python3.x/site-packages
    WSGIProcessGroup eng-game
    WSGIScriptAlias / /path/to/your/app/wsgi.py
    
    <Directory /path/to/your/app>
        Require all granted
    </Directory>
</VirtualHost>
```

---

## 🔧 系統服務配置

### systemd 服務檔案

#### 建立服務檔案
```bash
sudo nano /etc/systemd/system/eng-game.service
```

#### 服務配置
```ini
[Unit]
Description=English Game Flask Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn.conf.py "app:create_app()"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 啟用服務
```bash
sudo systemctl daemon-reload
sudo systemctl enable eng-game
sudo systemctl start eng-game
sudo systemctl status eng-game
```

---

## 🔒 安全配置

### SSL/TLS 憑證

#### 使用 Let's Encrypt
```bash
# 安裝 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 取得憑證
sudo certbot --nginx -d your-domain.com

# 自動更新
sudo crontab -e
# 加入以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

#### Nginx SSL 配置
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # 其他配置...
}
```

### 防火牆配置
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

---

## 📊 監控與日誌

### 應用程式日誌
```python
# 在 app.py 中配置日誌
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/eng-game.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('English Game startup')
```

### 系統監控
```bash
# 監控應用程式狀態
sudo systemctl status eng-game

# 查看日誌
sudo journalctl -u eng-game -f

# 監控系統資源
htop
df -h
free -h
```

---

## 🔄 更新部署

### 部署腳本
```bash
#!/bin/bash
# deploy.sh

echo "🚀 開始部署..."

# 停止服務
sudo systemctl stop eng-game

# 更新程式碼
git pull origin main

# 更新依賴
source venv/bin/activate
pip install -r requirements.txt

# 資料庫遷移
python init_db.py

# 重啟服務
sudo systemctl start eng-game

echo "✅ 部署完成！"
```

### 自動化部署
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.4
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.KEY }}
        script: |
          cd /path/to/your/app
          ./deploy.sh
```

---

## 🐛 故障排除

### 常見問題

#### 1. 埠號被佔用
```bash
# 檢查埠號使用情況
sudo netstat -tlnp | grep :5000

# 殺死佔用程序
sudo kill -9 <PID>
```

#### 2. 權限問題
```bash
# 修正檔案權限
sudo chown -R www-data:www-data /path/to/your/app
sudo chmod -R 755 /path/to/your/app
```

#### 3. 資料庫連線問題
```bash
# 檢查 MySQL 服務
sudo systemctl status mysql

# 檢查資料庫連線
mysql -u root -p -h 127.0.0.1
```

#### 4. WebSocket 連線問題
```bash
# 檢查防火牆設定
sudo ufw status

# 檢查 Nginx 配置
sudo nginx -t
```

---

## 📝 檢查清單

### 部署前檢查
- [ ] 資料庫已建立並初始化
- [ ] 環境變數已正確設定
- [ ] 依賴套件已安裝
- [ ] 防火牆已配置
- [ ] SSL 憑證已安裝

### 部署後檢查
- [ ] 應用程式正常啟動
- [ ] 網站可以正常訪問
- [ ] WebSocket 連線正常
- [ ] 資料庫連線正常
- [ ] 日誌記錄正常
- [ ] 監控系統正常

---

## 🎯 效能優化

### 資料庫優化
```sql
-- 建立索引
CREATE INDEX idx_questions_category ON questions(category);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_game_sessions_user_id ON game_sessions(user_id);
```

### 應用程式優化
```python
# 啟用快取
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# 使用快取裝飾器
@cache.memoize(timeout=300)
def get_questions(categories, difficulties):
    # 查詢邏輯
    pass
```

---

*最後更新：2024年12月*
*部署方式：純 Python，無需容器化* 