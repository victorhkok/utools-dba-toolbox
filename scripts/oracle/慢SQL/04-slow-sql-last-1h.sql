-- 近1h 慢SQL（执行>5s）
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$sql + elapsed
-- 提醒：5 秒阈值是 elapsed_time/executions > 5,000,000 微秒；last_active_time 是最后活跃时间，不是首次执行时间。

SELECT sql_id, executions,
       ROUND(elapsed_time / NULLIF(executions, 0) / 1000000, 2) AS avg_sec,
       ROUND(elapsed_time / 1000000, 2) AS total_sec,
       buffer_gets,
       SUBSTR(sql_text, 1, 200) AS sql_text
FROM   v$sql
WHERE  last_active_time >= SYSDATE - 1 / 24
  AND  executions > 0
  AND  elapsed_time / executions > 5000000
ORDER  BY avg_sec DESC;
