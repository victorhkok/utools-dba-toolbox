-- 执行计划（EXPLAIN）
-- 适用版本：4.x
-- 风险：只读
-- 说明：MySQL/Oracle模式区分
-- 备注：MySQL 模式用 EXPLAIN，Oracle 模式用 EXPLAIN PLAN FOR，需按租户模式区分。

EXPLAIN SELECT * FROM <TABLE> WHERE <CONDITION>;
