-- 慢查询日志分析（mysqldumpslow / pt-query-digest）
-- 适用版本：5.7+
-- 风险：只读
-- 说明：命令行工具
-- 大类：慢SQL / 小类：定位
-- shell: mysqldumpslow -s t -t 20 "<slow_log路径>"
-- shell: pt-query-digest --type slowlog "<slow_log路径>" | head -n 100
SHOW VARIABLES LIKE 'slow_query_log_file';
