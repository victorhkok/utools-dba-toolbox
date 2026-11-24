-- 1. 先确认会话（只读）：
SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO
FROM information_schema.PROCESSLIST
WHERE ID = <THREAD_ID>;
-- 2. 确认无误后再执行（危险）：
-- DANGER: KILL <THREAD_ID>;
