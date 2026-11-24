-- 长运行会话（>30min）
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$session + sql
-- 提醒：last_call_et 是当前调用已持续秒数，不是整个会话时长；>1800 秒即 30 分钟，勿把空闲会话（last_call_et 大但 status=INACTIVE）算进来。

SELECT sid, serial#, username, sql_id, event,
       last_call_et,
       ROUND(last_call_et / 60, 1) AS mins_running,
       ROUND((SYSDATE - logon_time) * 24 * 60, 1) AS mins_since_logon
FROM   v$session
WHERE  status = 'ACTIVE'
  AND  type = 'USER'
  AND  last_call_et > 1800
ORDER  BY last_call_et DESC;
