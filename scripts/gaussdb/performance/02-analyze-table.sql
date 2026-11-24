-- 1. 先确认未分析的表（只读）：
SELECT schemaname, tablename, last_analyze, n_live_tup FROM pg_stat_user_tables WHERE last_analyze IS NULL ORDER BY n_live_tup DESC LIMIT 20;
-- 2. 建议非高峰执行（谨慎）：
-- DANGER: ANALYZE <SCHEMA>.<TABLE>;
