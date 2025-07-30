-- 更新題目的分類關聯
UPDATE questions q 
JOIN categories c ON c.name = 'daily_conversation'
SET q.category_id = c.id 
WHERE q.category = '日常生活（Daily Conversation）';

UPDATE questions q 
JOIN categories c ON c.name = 'travel_transport'
SET q.category_id = c.id 
WHERE q.category = '旅遊與交通（Travel & Transport）';

UPDATE questions q 
JOIN categories c ON c.name = 'business_english'
SET q.category_id = c.id 
WHERE q.category = '商業英語（Business English）';

UPDATE questions q 
JOIN categories c ON c.name = 'campus_life'
SET q.category_id = c.id 
WHERE q.category = '校園生活（Campus Life）';

UPDATE questions q 
JOIN categories c ON c.name = 'health_medical'
SET q.category_id = c.id 
WHERE q.category = '健康與醫療（Health & Medical）'; 