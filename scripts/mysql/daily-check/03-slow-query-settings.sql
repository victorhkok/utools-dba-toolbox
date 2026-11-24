-- 慢查询开关与阈值
-- 适用版本：5.7+
-- 风险：只读
-- 说明：slow_query_log
-- 大类：日常巡检 / 小类：实例与状态
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
SHOW VARIABLES LIKE 'slow_query_log_file';
SHOW VARIABLES LIKE 'log_queries_not_using_indexes';
