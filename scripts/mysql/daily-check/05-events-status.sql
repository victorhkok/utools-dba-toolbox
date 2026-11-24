-- 定时任务 / EVENT 状态
-- 适用版本：5.7+
-- 风险：只读
-- 说明：SHOW EVENTS
-- 大类：日常巡检 / 小类：实例与状态
SHOW VARIABLES LIKE 'event_scheduler';
SHOW EVENTS;
SELECT EVENT_SCHEMA, EVENT_NAME, STATUS, LAST_EXECUTED FROM information_schema.EVENTS LIMIT 20;
