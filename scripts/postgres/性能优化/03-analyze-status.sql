-- 统计信息 / ANALYZE 状态
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_stat_user_tables。n_mod_since_analyze 大且 last_analyze 很旧，说明统计信息过期。
-- 大类：性能优化 / 小类：参数与缓存

SELECT schemaname, relname, n_live_tup, n_mod_since_analyze,
       last_analyze, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_mod_since_analyze DESC NULLS LAST
LIMIT 20;
