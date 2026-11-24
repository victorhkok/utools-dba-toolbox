SELECT schemaname, tablename,
  pg_table_size(schemaname || '.' || tablename) / 1024 / 1024 AS size_mb
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY size_mb DESC
LIMIT 20;
