-- 统计信息 / 优化器
-- 适用版本：8a
-- 风险：只读
-- 说明：ANALYZE
-- 备注：8a 的统计信息收集语法需在 8a 实测核对，ANALYZE 模板仅供参考。

SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS, UPDATE_TIME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema') ORDER BY UPDATE_TIME ASC LIMIT 20;
-- 如需收集统计信息（建议非高峰）：
-- ANALYZE TABLE <SCHEMA>.<TABLE>;
