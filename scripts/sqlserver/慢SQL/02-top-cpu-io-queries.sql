-- 最耗 CPU / IO 的查询
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.dm_exec_query_stats。dm_exec_query_stats 是缓存累计值，重启/缓存清理后会清零，对比要看 execution_count。
-- 大类：慢SQL / 小类：定位

SELECT TOP 20
       qs.total_worker_time / 1000 AS total_cpu_ms,
       qs.total_logical_reads, qs.total_logical_writes,
       qs.execution_count,
       SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1,
         ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(st.text)
           ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) + 1) AS query_text
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY qs.total_worker_time DESC;
