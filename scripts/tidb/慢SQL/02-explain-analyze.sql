-- EXPLAIN ANALYZE
-- 适用版本：6.x+
-- 风险：只读
-- 说明：TiDB 执行计划
-- 备注：TiDB 的 EXPLAIN ANALYZE 与 MySQL 8.0 类似，输出含各算子真实耗时。

EXPLAIN ANALYZE SELECT * FROM <TABLE> WHERE <CONDITION>;
