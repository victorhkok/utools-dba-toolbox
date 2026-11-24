-- ASH Top 等待事件
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$active_session_history
-- 提醒：v$active_session_history 是 1 秒采样，COUNT(*) 不是精确等待秒数，只能看占比；同样需 Diagnostic Pack 授权。

SELECT *
FROM   (SELECT event,
               wait_class,
               COUNT(*) AS samples,
               ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct
        FROM   v$active_session_history
        WHERE  sample_time >= SYSDATE - 1 / 24
          AND  event IS NOT NULL
        GROUP  BY event, wait_class
        ORDER  BY samples DESC)
WHERE  ROWNUM <= 20;
