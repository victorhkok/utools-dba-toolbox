SELECT query, calls,
  ROUND(total_exec_time::numeric / 1000, 2) AS total_sec,
  ROUND(mean_exec_time::numeric, 2) AS mean_ms, rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
