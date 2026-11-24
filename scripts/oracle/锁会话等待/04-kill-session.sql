-- 杀会话（ALTER SYSTEM KILL）
-- 适用版本：11g+
-- 风险：危险
-- 说明：先确认业务影响
-- 提醒：DANGER：先确认 sid+serial# 对应的是目标会话而非后台进程；KILL 后会话可能要等 PMON 清理回滚，勿重复 KILL。

-- 第 1 步：先确认要杀的会话（只读）：
SELECT sid, serial#, username, machine, program, status, sql_id, event
FROM   v$session
WHERE  sid = <sid>
  AND  serial# = <serial#>;

-- 第 2 步：确认无误后再执行（DANGER：会中断业务会话，RAC 需加 @inst_id）：
-- ALTER SYSTEM KILL SESSION '<sid>,<serial#>' IMMEDIATE;
-- RAC 写法：
-- ALTER SYSTEM KILL SESSION '<sid>,<serial#>,@<inst_id>' IMMEDIATE;
