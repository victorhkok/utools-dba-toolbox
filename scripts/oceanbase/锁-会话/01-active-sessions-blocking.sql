-- 活跃会话 / 阻塞
-- 适用版本：4.x
-- 风险：只读
-- 说明：GV$OB_PROCESSLIST
-- 备注：GV$OB_PROCESSLIST 列名需在 OB 4.x 实测核对，MySQL 模式与 Oracle 模式字段不同。

SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO
FROM oceanbase.GV$OB_PROCESSLIST
WHERE COMMAND != 'Sleep'
ORDER BY TIME DESC LIMIT 20;
