-- pg_stat_statements Top SQL
-- 适用版本：12+
-- 风险：只读
-- 说明：需开启扩展。需先 CREATE EXTENSION pg_stat_statements 并在 shared_preload_libraries 里加载，PG 12 列名是 total_time/mean_time。
-- 大类：慢SQL / 小类：定位

-- 前置（一次）：CREATE EXTENSION pg_stat_statements;
-- PG 13+ 用 total_exec_time / mean_exec_time；PG 12 用 total_time / mean_time
SELECT query, calls,
       round(total_exec_time::numeric, 2) AS total_exec_time_ms,
       round(mean_exec_time::numeric, 2) AS mean_exec_time_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
