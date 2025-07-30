# 🎨 前端介面使用說明

## 📋 概述

本專案提供了一個完整的現代化前端介面，使用 Bootstrap 5 和 jQuery 建立，包含遊戲主介面和管理後台。

---

## 🎮 遊戲主介面

### 功能特色

- **響應式設計** - 支援桌面和移動設備
- **現代化 UI** - 使用 Bootstrap 5 和自定義樣式
- **即時互動** - WebSocket 即時通訊
- **動畫效果** - 流暢的過渡動畫
- **深色模式支援** - 自動適應系統主題

### 主要頁面

#### 1. 首頁 (`/`)
- 歡迎介面
- 登入/註冊功能
- 遊戲介紹

#### 2. 遊戲介面
- 房間列表
- 遊戲房間
- 即時聊天
- 玩家列表
- 題目顯示
- 計時器

### 使用流程

1. **註冊/登入**
   - 點擊「註冊」或「登入」按鈕
   - 填寫必要資訊
   - 系統會自動記住登入狀態

2. **建立/加入房間**
   - 點擊「建立房間」設定遊戲參數
   - 或從房間列表選擇現有房間
   - 等待其他玩家加入

3. **開始遊戲**
   - 房間建立者可以開始遊戲
   - 系統會自動分配題目
   - 玩家在時間限制內答題

4. **即時互動**
   - 查看其他玩家狀態
   - 使用聊天功能
   - 即時查看分數

---

## 🔧 管理後台

### 功能特色

- **完整管理功能** - 題目、使用者、房間管理
- **統計圖表** - 使用 Chart.js 顯示數據
- **權限控制** - 管理員專用介面
- **即時監控** - 系統狀態監控

### 主要功能

#### 1. 儀表板
- 系統概覽
- 統計數據
- 最近活動
- 系統狀態

#### 2. 題目管理
- 查看所有題目
- 新增題目
- 編輯題目
- 刪除題目

#### 3. 使用者管理
- 查看使用者列表
- 管理使用者狀態
- 刪除使用者

#### 4. 房間管理
- 查看所有房間
- 監控房間狀態
- 管理房間

#### 5. 統計資料
- 題目分類統計
- 遊戲趨勢圖表
- 使用者活動分析

### 訪問方式

- 網址：`http://localhost:5000/admin`
- 需要管理員權限
- 使用管理員帳號登入

---

## 🎨 設計特色

### 色彩方案

```css
--primary-color: #4e73df    /* 主要藍色 */
--secondary-color: #858796  /* 次要灰色 */
--success-color: #1cc88a    /* 成功綠色 */
--warning-color: #f6c23e    /* 警告黃色 */
--danger-color: #e74a3b     /* 危險紅色 */
```

### 字體

- **主要字體**：Nunito
- **備用字體**：系統字體堆疊
- **圖示**：Font Awesome 6.4.0

### 動畫效果

- **懸停效果** - 按鈕和卡片懸停動畫
- **載入動畫** - 旋轉載入指示器
- **通知動畫** - 滑入通知效果
- **過渡動畫** - 平滑的頁面切換

---

## 📱 響應式設計

### 斷點設定

```css
/* 桌面 */
@media (min-width: 992px) { }

/* 平板 */
@media (max-width: 991px) { }

/* 手機 */
@media (max-width: 768px) { }
```

### 適配內容

- **導航欄** - 手機版折疊選單
- **表格** - 響應式表格設計
- **卡片** - 自適應卡片佈局
- **按鈕** - 觸控友善的按鈕大小

---

## 🔌 技術架構

### 前端技術棧

- **HTML5** - 語義化標籤
- **CSS3** - 現代化樣式
- **Bootstrap 5** - UI 框架
- **jQuery 3.7.1** - JavaScript 庫
- **Socket.IO** - 即時通訊
- **Chart.js** - 圖表庫

### 檔案結構

```
public/
├── index.html          # 遊戲主介面
├── admin.html          # 管理後台
├── css/
│   └── style.css       # 自定義樣式
└── js/
    ├── app.js          # 遊戲邏輯
    └── admin.js        # 管理後台邏輯
```

### 依賴 CDN

```html
<!-- Bootstrap 5 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js">

<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>

<!-- Font Awesome -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Socket.IO -->
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

---

## 🚀 快速開始

### 1. 啟動後端服務

```bash
python run.py
```

### 2. 訪問前端介面

- **遊戲介面**：http://localhost:5000
- **管理後台**：http://localhost:5000/admin

### 3. 測試功能

1. 註冊新帳號
2. 建立遊戲房間
3. 邀請朋友加入
4. 開始遊戲測試

---

## 🎯 自定義設定

### 修改主題色彩

編輯 `public/css/style.css`：

```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    /* 其他色彩變數 */
}
```

### 修改 API 端點

編輯 JavaScript 檔案中的 `apiBase`：

```javascript
this.apiBase = 'http://your-server:port/api';
```

### 自定義樣式

在 `public/css/style.css` 中添加：

```css
/* 自定義樣式 */
.your-custom-class {
    /* 樣式定義 */
}
```

---

## 🔧 開發指南

### 新增功能

1. **HTML 結構** - 在對應的 HTML 檔案中添加元素
2. **CSS 樣式** - 在 `style.css` 中添加樣式
3. **JavaScript 邏輯** - 在對應的 JS 檔案中添加功能

### 除錯技巧

1. **瀏覽器開發者工具** - 檢查 Console 錯誤
2. **網路面板** - 監控 API 請求
3. **元素檢查** - 檢查 DOM 結構

### 效能優化

1. **圖片優化** - 使用適當的圖片格式和大小
2. **CSS 優化** - 合併和壓縮 CSS 檔案
3. **JavaScript 優化** - 減少 DOM 操作

---

## 📞 支援

### 常見問題

1. **WebSocket 連線失敗**
   - 檢查後端服務是否運行
   - 確認防火牆設定

2. **樣式顯示異常**
   - 清除瀏覽器快取
   - 檢查 CSS 檔案路徑

3. **API 請求失敗**
   - 檢查 API 端點設定
   - 確認認證 token

### 聯絡方式

- **技術支援**：查看專案文件
- **功能建議**：提交 Issue
- **Bug 回報**：提供詳細錯誤資訊

---

## 📄 授權

本前端介面遵循與後端相同的授權條款。

---

*最後更新：2024年12月*
*版本：1.0.0* 