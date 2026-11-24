-- 未使用索引（sys.schema_unused_indexes）
-- 适用版本：5.7+
-- 风险：只读
-- 说明：sys 库
-- 大类：性能优化 / 小类：索引
SELECT * FROM sys.schema_unused_indexes LIMIT 50;
