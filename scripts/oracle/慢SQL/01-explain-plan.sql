-- 查看执行计划（EXPLAIN PLAN）
-- 适用版本：11g+
-- 风险：只读
-- 说明：DBMS_XPLAN
-- 提醒：EXPLAIN PLAN 是预估计划，不代表真实执行；要真实行数用 DISPLAY_CURSOR 或加 GATHER_PLAN_STATISTICS Hint。

-- 模板：把 <你的SQL> 换成要分析的语句（不带分号结尾的分号外写法见下）
EXPLAIN PLAN FOR
SELECT * FROM <schema>.<table_name> WHERE <condition>;

SELECT * FROM TABLE(DBMS_XPLAN.display);
