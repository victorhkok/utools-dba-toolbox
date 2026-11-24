-- 阻塞链（sys.dm_exec_requests）
-- 适用版本：2016+
-- 风险：只读
-- 说明：blocking_session_id。blocking_session_id 是直接阻塞者，链的根因要顺着 blocking_session_id 往上追。
-- 大类：锁 / 会话 / 小类：锁

SELECT TOP 20
       r.session_id, r.blocking_session_id, r.wait_type, r.wait_time,
       r.status, r.command,
       SUBSTRING(t.text, (r.statement_start_offset / 2) + 1,
         ((CASE r.statement_end_offset WHEN -1 THEN DATALENGTH(t.text)
           ELSE r.statement_end_offset END - r.statement_start_offset) / 2) + 1) AS query_text
FROM sys.dm_exec_requests AS r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) AS t
WHERE r.blocking_session_id <> 0
ORDER BY r.wait_time DESC;
