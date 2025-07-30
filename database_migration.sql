-- 英文對答遊戲資料庫遷移腳本
-- 將 questions 表格的 category 欄位遷移到新的 categories 表格

-- 1. 建立新的 categories 表格
CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 建立分類資料
INSERT INTO categories (id, name, display_name, description) VALUES
(UUID(), 'daily_conversation', 'Daily Conversation', 'Daily conversation and expressions'),
(UUID(), 'travel_transport', 'Travel & Transport', 'Travel and transportation vocabulary'),
(UUID(), 'business_english', 'Business English', 'Business and workplace English'),
(UUID(), 'campus_life', 'Campus Life', 'School and campus life expressions'),
(UUID(), 'health_medical', 'Health & Medical', 'Health and medical vocabulary');

-- 3. 在 questions 表格中新增 category_id 欄位
ALTER TABLE questions ADD COLUMN category_id VARCHAR(36);

-- 4. 更新 questions 表格的 category_id
UPDATE questions q 
JOIN categories c ON 
    CASE 
        WHEN q.category = '日常生活（Daily Conversation）' THEN c.name = 'daily_conversation'
        WHEN q.category = '旅遊與交通（Travel & Transport）' THEN c.name = 'travel_transport'
        WHEN q.category = '商業英語（Business English）' THEN c.name = 'business_english'
        WHEN q.category = '校園生活（Campus Life）' THEN c.name = 'campus_life'
        WHEN q.category = '健康與醫療（Health & Medical）' THEN c.name = 'health_medical'
    END
SET q.category_id = c.id;

-- 5. 建立外鍵約束
ALTER TABLE questions 
ADD CONSTRAINT fk_questions_category 
FOREIGN KEY (category_id) REFERENCES categories(id);

-- 6. 建立索引
CREATE INDEX idx_questions_category_id ON questions(category_id);

-- 7. 移除舊的 category 欄位（可選，建議先保留一段時間）
-- ALTER TABLE questions DROP COLUMN category;

-- 8. 移除舊的索引（如果存在）
-- DROP INDEX IF EXISTS idx_questions_category ON questions; 