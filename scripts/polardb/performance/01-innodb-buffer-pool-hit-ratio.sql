-- 命中率 = 1 - Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';
