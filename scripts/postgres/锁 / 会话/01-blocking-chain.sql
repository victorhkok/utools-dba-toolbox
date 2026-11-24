-- 阻塞锁链（pg_blocking_pids）
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_stat_activity。pg_blocking_pids() 返回阻塞该会话的 pid 数组，根因一般是排头的 blocking_pid。
-- 大类：锁 / 会话 / 小类：锁

SELECT blocked.pid AS blocked_pid, blocked.usename AS blocked_user,
       blocked.application_name, blocked.state,
       now() - blocked.query_start AS blocked_duration,
       blocking.pid AS blocking_pid, blocking.usename AS blocking_user,
       left(blocked.query, 200) AS blocked_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking
  ON blocking.pid = ANY (pg_blocking_pids(blocked.pid))
WHERE cardinality(pg_blocking_pids(blocked.pid)) > 0
ORDER BY blocked_duration DESC
LIMIT 20;
