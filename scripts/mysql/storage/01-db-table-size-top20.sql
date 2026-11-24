-- 库 / 表大小 Top 20
-- 适用版本：5.7+
-- 风险：只读
-- 说明：information_schema.TABLES
-- 大类：空间 / 存储 / 小类：空间
SELECT TABLE_SCHEMA, TABLE_NAME, ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb, ROUND(SUM(DATA_LENGTH) / 1024 / 1024, 2) AS data_mb, ROUND(SUM(INDEX_LENGTH) / 1024 / 1024, 2) AS index_mb, SUM(TABLE_ROWS) AS rows_est FROM information_schema.TABLES GROUP BY TABLE_SCHEMA, TABLE_NAME ORDER BY size_mb DESC LIMIT 20;
