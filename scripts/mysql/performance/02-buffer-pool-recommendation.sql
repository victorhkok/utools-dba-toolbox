-- Buffer Pool 建议值
-- 适用版本：5.7+
-- 风险：只读
-- 说明：按内存 70-80% 估算
-- 大类：性能优化 / 小类：参数与内存
SELECT @@innodb_buffer_pool_size / 1024 / 1024 / 1024 AS buffer_pool_gb;
SHOW VARIABLES LIKE 'innodb_buffer_pool_instances';
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_total';
