-- 膨胀索引 / bloat 评估
-- 适用版本：12+
-- 风险：只读
-- 说明：pgstattuple。pgstatindex 一次只能查一个索引，全库 bloat 需循环或用 pgstattuple 的近似估算查询。
-- 大类：性能优化 / 小类：索引

-- 先确认扩展：pgstattuple 不在 PG 核心里
SELECT * FROM pg_extension WHERE extname = 'pgstattuple';
-- 单个索引评估（替换参数为索引名）：
-- SELECT * FROM pgstatindex('<index_name>');
-- 无扩展时的替代：只看索引大小排序，再结合表膨胀判断
SELECT schemaname, relname AS table_name, indexrelname AS index_name,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;
