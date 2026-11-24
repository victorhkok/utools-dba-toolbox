-- 杀会话（KILL CONNECTION）
-- 适用版本：5.7+
-- 风险：危险
-- 说明：先确认
-- 大类：锁 / 会话 / 小类：锁
-- 先查，再杀：
SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO FROM information_schema.PROCESSLIST WHERE TIME > 300 ORDER BY TIME DESC LIMIT 20;
-- DANGER: 先确认该连接的业务影响，再执行下面一行，<connection_id> 填上面查到的 ID：
-- KILL CONNECTION <connection_id>;
