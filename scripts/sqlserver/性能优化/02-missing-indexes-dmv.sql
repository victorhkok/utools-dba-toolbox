-- 缺失索引 DMV
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.dm_db_missing_index_details。DMV 只给建议，建索引前要核对表大小、写比例和已有索引，避免重复建。
-- 大类：性能优化 / 小类：DMV

SELECT TOP 20
       migs.avg_total_user_cost * migs.avg_user_impact
         * (migs.user_seeks + migs.user_scans) AS improvement_measure,
       mid.statement AS table_name,
       mid.equality_columns, mid.inequality_columns, mid.included_columns
FROM sys.dm_db_missing_index_groups AS mig
INNER JOIN sys.dm_db_missing_index_group_stats AS migs
  ON migs.group_handle = mig.index_group_handle
INNER JOIN sys.dm_db_missing_index_details AS mid
  ON mig.index_handle = mid.index_handle
ORDER BY improvement_measure DESC;
