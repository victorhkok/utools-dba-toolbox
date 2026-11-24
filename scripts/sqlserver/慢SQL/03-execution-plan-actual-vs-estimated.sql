-- 执行计划（实际 vs 预估）
-- 适用版本：2016+
-- 风险：只读
-- 说明：SSMS / DMV。DMV 给的是缓存的预估计划，真实执行耗时要看 SSMS 的实际执行计划。
-- 大类：慢SQL / 小类：定位

SELECT TOP 20
       qs.plan_handle, qs.execution_count,
       SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1,
         ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(st.text)
           ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) + 1) AS query_text
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY qs.execution_count DESC;
-- 取某条计划的 XML（替换参数为 plan_handle 的二进制值，需在 SSMS 里转）：
-- SELECT query_plan FROM sys.dm_exec_query_plan(<plan_handle>);
-- 实际执行计划在 SSMS 里用 Ctrl+M 开“包括实际执行计划”再跑查询
