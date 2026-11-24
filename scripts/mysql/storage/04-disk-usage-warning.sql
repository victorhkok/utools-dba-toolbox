-- 磁盘使用率预警
-- 适用版本：5.7+
-- 风险：只读
-- 说明：df + 表大小
-- 大类：空间 / 存储 / 小类：空间
SELECT TABLE_SCHEMA, ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 / 1024, 2) AS total_gb FROM information_schema.TABLES GROUP BY TABLE_SCHEMA ORDER BY total_gb DESC LIMIT 20;
