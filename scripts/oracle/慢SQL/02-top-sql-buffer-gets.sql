-- Top SQL by Buffer Gets
-- 适用版本：11g+
-- 风险：只读
-- 说明：逻辑读最高
-- 提醒：逻辑读高不一定是慢 SQL，要结合 avg_sec 和执行次数看；先看 gets_per_exec 再决定是否优化。

SELECT *
FROM   (SELECT sql_id, executions,
               buffer_gets,
               ROUND(buffer_gets / NULLIF(executions, 0), 0) AS gets_per_exec,
               ROUND(elapsed_time / 1000000, 2) AS elapsed_sec,
               SUBSTR(sql_text, 1, 200) AS sql_text
        FROM   v$sql
        ORDER  BY buffer_gets DESC)
WHERE  ROWNUM <= 20;
