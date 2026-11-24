-- Query Store Top SQL（2016+）
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.query_store_runtime_stats。Query Store 需先开启（ALTER DATABASE SET QUERY_STORE = ON），没开时这些视图是空的。
-- 大类：慢SQL / 小类：定位

-- 前置：Query Store 需开启，查 sys.database_query_store_options 确认
SELECT state_desc FROM sys.database_query_store_options;
SELECT TOP 20
       q.query_id,
       LEFT(qt.query_sql_text, 200) AS query_text,
       rs.avg_duration AS avg_duration_us,
       rs.count_executions,
       rs.avg_cpu_time, rs.avg_logical_io_reads
FROM sys.query_store_query AS q
JOIN sys.query_store_query_text AS qt
  ON qt.query_text_id = q.query_text_id
JOIN sys.query_store_plan AS p
  ON p.query_id = q.query_id
JOIN sys.query_store_runtime_stats AS rs
  ON rs.plan_id = p.plan_id
ORDER BY rs.avg_duration DESC;
