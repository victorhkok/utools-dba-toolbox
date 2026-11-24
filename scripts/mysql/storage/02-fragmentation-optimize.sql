-- 碎片率与 OPTIMIZE 评估
-- 适用版本：5.7+
-- 风险：谨慎
-- 说明：OPTIMIZE 会锁表（8.0 在线部分）
-- 大类：空间 / 存储 / 小类：空间
SELECT TABLE_SCHEMA, TABLE_NAME, ROUND(DATA_FREE / 1024 / 1024, 2) AS data_free_mb, ROUND(DATA_FREE / NULLIF(DATA_LENGTH + INDEX_LENGTH, 0) * 100, 2) AS free_pct FROM information_schema.TABLES WHERE DATA_FREE > 0 ORDER BY DATA_FREE DESC LIMIT 20;
-- 评估后、非高峰再执行：OPTIMIZE TABLE <db>.<table>;
