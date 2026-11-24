-- 正在等待锁的会话（官方手册示例：pg_stat_activity WHERE waiting = true）：
SELECT datname, usename, pid, state, waiting, now() - query_start AS wait_duration, left(query, 200) AS query
FROM pg_stat_activity WHERE waiting = true ORDER BY query_start;
-- 锁持有情况：
SELECT locktype, mode, granted, count(*) AS cnt FROM pg_locks GROUP BY locktype, mode, granted ORDER BY cnt DESC;
