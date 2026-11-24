-- 缓存命中率（heap / index）
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_statio_user_tables。heap 命中率低于 99% 且读盘大时先看 shared_buffers 和热点表。
-- 大类：性能优化 / 小类：参数与缓存

SELECT schemaname, relname,
       heap_blks_read, heap_blks_hit,
       round(100.0 * heap_blks_hit / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS heap_hit_pct,
       idx_blks_read, idx_blks_hit,
       round(100.0 * idx_blks_hit / NULLIF(idx_blks_hit + idx_blks_read, 0), 2) AS idx_hit_pct
FROM pg_statio_user_tables
ORDER BY heap_blks_read DESC
LIMIT 20;
