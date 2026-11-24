-- 冗余 / 重复索引
-- 适用版本：5.7+
-- 风险：只读
-- 说明：sys.schema_redundant_indexes
-- 大类：性能优化 / 小类：索引
SELECT * FROM sys.schema_redundant_indexes LIMIT 50;
