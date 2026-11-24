-- 关键参数速查（innodb_buffer_pool_size 等）
-- 适用版本：5.7+
-- 风险：只读
-- 说明：SHOW VARIABLES
-- 大类：性能优化 / 小类：参数与内存
SHOW VARIABLES WHERE Variable_name IN ('innodb_buffer_pool_size', 'innodb_log_file_size', 'innodb_flush_log_at_trx_commit', 'max_connections', 'innodb_buffer_pool_instances', 'tmp_table_size', 'max_heap_table_size', 'sort_buffer_size', 'join_buffer_size', 'innodb_io_capacity', 'innodb_flush_method');
