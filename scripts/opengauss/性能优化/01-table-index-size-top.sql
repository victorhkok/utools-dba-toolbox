SELECT schemaname, relname, pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
  pg_size_pretty(pg_table_size(relid)) AS table_size,
  pg_size_pretty(pg_indexes_size(relid)) AS indexes_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC LIMIT 20;
