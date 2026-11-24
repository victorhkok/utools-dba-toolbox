-- InnoDB Buffer Pool 命中率
-- 适用版本：5.7+
-- 风险：只读
-- 说明：Innodb_buffer_pool_read%
-- 大类：日常巡检 / 小类：健康指标
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';
SELECT ROUND(100 * (1 - SUM(CASE WHEN VARIABLE_NAME = 'Innodb_buffer_pool_reads' THEN VARIABLE_VALUE ELSE 0 END) / NULLIF(SUM(CASE WHEN VARIABLE_NAME = 'Innodb_buffer_pool_read_requests' THEN VARIABLE_VALUE ELSE 0 END), 0)), 2) AS buffer_pool_hit_pct FROM performance_schema.global_status WHERE VARIABLE_NAME IN ('Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests');
