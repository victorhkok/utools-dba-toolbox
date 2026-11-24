-- 统计信息 / 直方图（8.0+）
-- 适用版本：8.0+
-- 风险：只读
-- 说明：information_schema.COLUMN_STATISTICS
-- 大类：性能优化 / 小类：参数与内存
SELECT SCHEMA_NAME, TABLE_NAME, COLUMN_NAME, HISTOGRAM FROM information_schema.COLUMN_STATISTICS LIMIT 50;
