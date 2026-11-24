-- 1. 先确认（只读）：
SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, LEFT(INFO, 200) AS SQL_TEXT FROM information_schema.PROCESSLIST WHERE ID = <ID>;
-- 2. 确认无误后再执行（危险）：
-- DANGER: KILL <ID>;
-- 只杀查询、不断连接可用：-- DANGER: KILL QUERY <ID>;
