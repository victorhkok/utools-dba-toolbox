-- 1. 先确认 binlog 与备份窗口（只读）：
SHOW BINARY LOGS;
SHOW GLOBAL VARIABLES LIKE 'binlog_expire_logs_seconds';
-- 2. 恢复为危险操作：PolarDB 无 SQL 恢复命令，在控制台按备份集 + 时间点恢复，优先恢复到新实例、核对后再切换；恢复前先在测试集群完整演练一次：
-- DANGER: 控制台 > 备份恢复 > 按时间点恢复到新实例（勿直接覆盖原集群）；
