-- KILL 会话
-- 适用版本：2016+
-- 风险：危险
-- 说明：KILL spid。KILL 前先确认 spid、登录名和正在跑的命令，杀掉后事务要回滚。
-- 大类：锁 / 会话 / 小类：锁

-- 第 1 步：先确认要杀的会话
SELECT session_id, login_name, host_name, program_name, status, command,
       cpu_time, reads, writes
FROM sys.dm_exec_sessions
WHERE session_id = <spid>;
-- DANGER：确认 spid 无误后再取消注释执行，KILL 会回滚该会话的事务
-- KILL <spid>;
