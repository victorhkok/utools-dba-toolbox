-- 1. 先确认（只读查询）：
SELECT pid, usename, datname, state, query_start, query FROM sys_stat_activity WHERE pid = <PID>;
-- 2. 确认无误后再执行（危险）：
-- DANGER: SELECT pg_terminate_backend(<PID>);
