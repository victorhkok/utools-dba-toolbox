SELECT schemaname, relname, n_live_tup, n_dead_tup,
  round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
  last_vacuum, last_autovacuum, last_analyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 0 ORDER BY n_dead_tup DESC LIMIT 20;
