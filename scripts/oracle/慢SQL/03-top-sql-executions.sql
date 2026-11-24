-- Top SQL by Executions
-- 适用版本：11g+
-- 风险：只读
-- 说明：执行次数最多
-- 提醒：执行次数多、单次不慢的 SQL 也值得优化，累计耗时可能最大；注意 v$sql_text 可能被截断。

SELECT *
FROM   (SELECT sql_id, executions,
               ROUND(elapsed_time / NULLIF(executions, 0) / 1000000, 2) AS avg_sec,
               buffer_gets, disk_reads,
               SUBSTR(sql_text, 1, 200) AS sql_text
        FROM   v$sql
        ORDER  BY executions DESC)
WHERE  ROWNUM <= 20;
