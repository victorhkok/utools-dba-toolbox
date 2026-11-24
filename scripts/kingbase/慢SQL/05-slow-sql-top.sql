SELECT query, calls, total_time, mean_time, rows, shared_blks_hit, shared_blks_read
FROM sys_stat_statements
ORDER BY total_time DESC
LIMIT 10;
