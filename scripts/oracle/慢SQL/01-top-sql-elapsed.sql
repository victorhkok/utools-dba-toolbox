-- Top SQL by Elapsed Time
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$sql / AWR Top SQL
-- 提醒：elapsed_time 单位是微秒；v$sql 是共享池累计值，实例重启后清零，长期 Top 以 AWR 为准。

SELECT *
FROM   (SELECT sql_id, executions,
               ROUND(elapsed_time / 1000000, 2) AS elapsed_sec,
               ROUND(elapsed_time / NULLIF(executions, 0) / 1000000, 2) AS avg_sec,
               buffer_gets, disk_reads,
               SUBSTR(sql_text, 1, 200) AS sql_text
        FROM   v$sql
        ORDER  BY elapsed_time DESC)
WHERE  ROWNUM <= 20;
