-- QPS / TPS 趋势
-- 适用版本：5.7+
-- 风险：只读
-- 说明：Questions / Com_commit
-- 大类：日常巡检 / 小类：健康指标
SHOW GLOBAL STATUS LIKE 'Questions';
SHOW GLOBAL STATUS LIKE 'Com_commit';
SHOW GLOBAL STATUS LIKE 'Com_rollback';
SHOW GLOBAL STATUS LIKE 'Uptime';
