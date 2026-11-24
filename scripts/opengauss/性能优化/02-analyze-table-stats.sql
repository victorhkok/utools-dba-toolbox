-- 1. 先确认统计信息是否过期（只读）：
SELECT schemaname, relname, last_analyze, last_autoanalyze, n_mod_since_analyze
FROM pg_stat_user_tables WHERE schemaname = '<SCHEMA>' AND relname = '<TABLE>';
-- 2. 确认后再执行（建议非高峰）：
-- DANGER: ANALYZE <SCHEMA>.<TABLE>;
