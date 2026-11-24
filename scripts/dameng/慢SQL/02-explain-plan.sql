-- 执行计划（EXPLAIN）
-- 适用版本：DM8+
-- 风险：只读
-- 说明：DM EXPLAIN
-- 备注：DM8 支持 EXPLAIN，输出格式与 Oracle 的 DBMS_XPLAN 不同，需在 DM8 实测核对。

EXPLAIN SELECT * FROM <SCHEMA>.<TABLE> WHERE <CONDITION>;
