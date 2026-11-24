-- 索引基数与选择性
-- 适用版本：5.7+
-- 风险：只读
-- 说明：SHOW INDEX
-- 大类：性能优化 / 小类：索引
SHOW INDEX FROM <db>.<table>;
SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, COLUMN_NAME, CARDINALITY FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = '<db>' AND TABLE_NAME = '<table>' LIMIT 50;
