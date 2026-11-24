-- 杀会话
-- 适用版本：DM8+
-- 风险：危险
-- 说明：SP_CLOSE_SESSION
-- 备注：SP_CLOSE_SESSION 需 DBA 权限，杀会话前务必确认业务影响。

-- 1. 先确认（只读查询）：
SELECT SESS_ID, USERNAME, CLIENT_IP, SQL_TEXT FROM V$SESSIONS WHERE SESS_ID = <SESS_ID>;
-- 2. 确认无误后再执行（危险）：
-- DANGER: SP_CLOSE_SESSION(<SESS_ID>);
