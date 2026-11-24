-- 统计信息过期
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.stats。modification_counter 大且 last_updated 很旧，说明统计信息过期，UPDATE STATISTICS 前先评估。
-- 大类：性能优化 / 小类：DMV

SELECT TOP 20
       OBJECT_NAME(s.object_id) AS table_name,
       s.name AS stats_name, s.auto_created, s.user_created,
       STATS_DATE(s.object_id, s.stats_id) AS last_updated,
       p.modification_counter, p.rows, p.rows_sampled
FROM sys.stats AS s
CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) AS p
ORDER BY last_updated ASC;
