SELECT unique_sql_id, query, n_calls,
  total_elapse_time / 1000 AS total_ms,
  total_elapse_time / NULLIF(n_calls, 0) / 1000 AS avg_ms
FROM dbe_perf.statement
ORDER BY total_elapse_time DESC
LIMIT 10;
