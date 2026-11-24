-- SGA / PGA 使用与建议
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$sga, v$pga_target_advice
-- 提醒：v$pga_target_advice 只在 PGA_AGGREGATE_TARGET 非 0 时有意义；SGA 改参数要重启或 ALTER SYSTEM，勿直接按建议值改生产。

SELECT name, ROUND(value / 1024 / 1024, 2) AS mb
FROM   v$sga;

SELECT pga_target_for_estimate / 1024 / 1024 AS pga_target_mb,
       estd_pga_cache_hit_percentage,
       estd_overalloc_count
FROM   v$pga_target_advice
ORDER  BY pga_target_for_estimate;

SELECT name, value
FROM   v$pgastat
WHERE  name IN ('total PGA allocated', 'total PGA inuse', 'maximum PGA allocated');
