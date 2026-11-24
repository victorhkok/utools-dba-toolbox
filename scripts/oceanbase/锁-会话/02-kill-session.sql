-- 杀会话（KILL）
-- 适用版本：4.x
-- 风险：危险
-- 说明：KILL id
-- 备注：OB 的 KILL 语法与 MySQL 兼容，Oracle 模式需按租户模式核对，杀会话前务必确认业务影响。

-- 1. 先确认（只读查询）：
SELECT ID, USER, HOST, COMMAND, TIME, INFO FROM oceanbase.GV$OB_PROCESSLIST WHERE ID = <ID>;
-- 2. 确认无误后再执行（危险）：
-- DANGER: KILL <ID>;
