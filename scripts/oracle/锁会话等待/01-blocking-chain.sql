-- 当前阻塞锁链
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$lock + v$session blocking
-- 提醒：blocking_session 为空不代表没锁，可能是行锁在等 TX；先找根阻塞者（blocking_session 为空的那行），不要先杀等待者。

SELECT sid, serial#, username, machine, program, status,
       blocking_session, blocking_session_serial#,
       event, sql_id,
       ROUND((SYSDATE - logon_time) * 24 * 60, 1) AS mins_since_logon
FROM   v$session
WHERE  blocking_session IS NOT NULL
   OR  sid IN (SELECT blocking_session FROM v$session WHERE blocking_session IS NOT NULL)
ORDER  BY blocking_session NULLS FIRST, sid;

-- 锁详情（v$lock）：
SELECT l.sid, l.type, l.lmode, l.request, l.block, s.username
FROM   v$lock l
       JOIN v$session s ON l.sid = s.sid
WHERE  l.block = 1 OR l.request > 0
ORDER  BY l.sid;
