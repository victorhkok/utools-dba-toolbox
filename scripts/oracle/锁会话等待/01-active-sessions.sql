-- 活跃会话 Top
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$session status=ACTIVE
-- 提醒：ACTIVE 只表示此刻在跑 SQL，不等于长耗时；结合 sql_id 和 event 看，不要只按 logon_time 排序就杀。

SELECT *
FROM   (SELECT sid, serial#, username, machine, program, status,
               event, sql_id,
               ROUND((SYSDATE - logon_time) * 24 * 60, 1) AS mins_since_logon
        FROM   v$session
        WHERE  status = 'ACTIVE'
          AND  type = 'USER'
        ORDER  BY logon_time)
WHERE  ROWNUM <= 20;
