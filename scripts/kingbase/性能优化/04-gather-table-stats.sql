-- 1. 先确认表上次分析时间（只读）：
SELECT schemaname, relname, last_analyze, last_autoanalyze, n_live_tup
FROM sys_stat_user_tables
WHERE schemaname = '<SCHEMA>' AND relname = '<TABLE>';
-- 2. 确认后在非高峰执行（谨慎）：
-- DANGER: ANALYZE <SCHEMA>.<TABLE>;
