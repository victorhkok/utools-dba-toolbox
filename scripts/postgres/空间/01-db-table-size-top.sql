-- 库 / 表大小 Top
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_database_size。pg_total_relation_size 含表+索引+TOAST，单看表大小用 pg_relation_size。
-- 大类：空间 / 小类：空间

SELECT datname, pg_size_pretty(pg_database_size(datname)) AS db_size
FROM pg_database
ORDER BY pg_database_size(datname) DESC
LIMIT 20;
SELECT schemaname, relname,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
       pg_size_pretty(pg_relation_size(relid)) AS table_size,
       pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;
