-- 死锁图（Extended Events）
-- 适用版本：2016+
-- 风险：只读
-- 说明：xml_deadlock_report。死锁图在 system_health 会话的 ring_buffer 里，XML 需解析 xml_deadlock_report 事件。
-- 大类：锁 / 会话 / 小类：锁

SELECT CAST(xet.target_data AS XML) AS xe_data
FROM sys.dm_xe_session_targets AS xet
JOIN sys.dm_xe_sessions AS xe
  ON xe.address = xet.event_session_address
WHERE xe.name = 'system_health'
  AND xet.target_name = 'ring_buffer';
-- 在返回的 XML 里找 xml_deadlock_report 事件；也可以在 SSMS 的扩展事件里直接看 system_health
