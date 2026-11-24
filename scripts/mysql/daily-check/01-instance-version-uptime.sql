-- 实例状态 / 版本 / uptime
-- 适用版本：5.7+
-- 风险：只读
-- 说明：SHOW GLOBAL STATUS
-- 大类：日常巡检 / 小类：实例与状态
SELECT VERSION() AS version;
SHOW GLOBAL STATUS LIKE 'Uptime';
SHOW GLOBAL STATUS LIKE 'Threads_connected';
