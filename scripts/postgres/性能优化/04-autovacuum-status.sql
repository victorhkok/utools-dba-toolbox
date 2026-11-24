-- 自动 VACUUM 状态
-- 适用版本：12+
-- 风险：只读
-- 说明：autovacuum。autovacuum 关了或 long-running 事务堵住时，死元组会一直涨。
-- 大类：性能优化 / 小类：参数与缓存

SELECT name, setting, unit
FROM pg_settings
WHERE name LIKE 'autovacuum%'
ORDER BY name;
SELECT schemaname, relname, last_autovacuum, last_autoanalyze,
       autovacuum_count, autoanalyze_count
FROM pg_stat_user_tables
ORDER BY last_autovacuum NULLS FIRST
LIMIT 20;
