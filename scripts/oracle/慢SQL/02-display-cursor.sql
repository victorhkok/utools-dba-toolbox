-- 真实执行计划（DBMS_XPLAN.DISPLAY_CURSOR）
-- 适用版本：11g+
-- 风险：只读
-- 说明：带A-Rows / Buffers
-- 提醒：'ALLSTATS LAST' 只有 SQL 带 /*+ GATHER_PLAN_STATISTICS */ 或 statistics_level=ALL 时才有 A-Rows/Buffers，否则只显示预估。

SELECT * FROM TABLE(DBMS_XPLAN.display_cursor('<sql_id>', <child_number>, 'ALLSTATS LAST'));

-- 查该 SQL 的 child_number：
SELECT sql_id, child_number, executions, plan_hash_value
FROM   v$sql
WHERE  sql_id = '<sql_id>'
ORDER  BY child_number;
