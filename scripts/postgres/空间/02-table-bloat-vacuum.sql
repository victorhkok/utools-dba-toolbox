-- 表膨胀 / VACUUM 建议
-- 适用版本：12+
-- 风险：谨慎
-- 说明：VACUUM / VACUUM FULL 区分。VACUUM 不锁表，VACUUM FULL 会独占锁并重写表，两者不要混用。
-- 大类：空间 / 小类：空间

-- 第 1 步：先看死元组和上次 VACUUM
SELECT schemaname, relname, n_live_tup, n_dead_tup,
       last_vacuum, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;
-- 普通 VACUUM 不锁表，可在线跑（替换表名）：
-- VACUUM (VERBOSE, ANALYZE) <schema_name>.<table_name>;
-- DANGER：VACUUM FULL 会重写整张表、独占锁、需额外磁盘空间，非高峰+确认后再跑
-- VACUUM FULL <schema_name>.<table_name>;
