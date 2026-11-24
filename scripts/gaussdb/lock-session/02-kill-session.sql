-- 1. 先确认（只读，华为云官方示例）：
SELECT datname, usename, state, pid FROM pg_stat_activity WHERE pid = <PID>;
-- 2. 确认无误后再执行（危险，华为云官方示例）：
-- DANGER: SELECT pg_terminate_backend(<PID>);
