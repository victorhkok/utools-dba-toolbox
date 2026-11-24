-- 连接数 / 最大连接
-- 适用版本：5.7+
-- 风险：只读
-- 说明：Threads_connected
-- 大类：日常巡检 / 小类：实例与状态
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Threads_running';
SHOW VARIABLES LIKE 'max_connections';
SELECT COUNT(*) AS processlist_count FROM information_schema.PROCESSLIST;
