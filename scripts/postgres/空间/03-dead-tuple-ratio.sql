-- 死元组比例
-- 适用版本：12+
-- 风险：只读
-- 说明：n_dead_tup。死元组占比高且 autovacuum 没跟上时，先查长事务是否堵住了 VACUUM。
-- 大类：空间 / 小类：空间

SELECT schemaname, relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
       last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;
