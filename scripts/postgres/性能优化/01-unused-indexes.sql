-- 未使用索引
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_stat_user_indexes idx_scan=0。idx_scan=0 只说明统计周期内没用过，删前确认统计周期够长且不是唯一约束索引。
-- 大类：性能优化 / 小类：索引

SELECT schemaname, relname AS table_name, indexrelname AS index_name,
       idx_scan, pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE 'pg_%'
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;
