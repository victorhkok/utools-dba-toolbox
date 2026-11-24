-- DG 切换演练（Switchover）
-- 适用版本：11g+
-- 风险：危险
-- 说明：演练前停写确认
-- 提醒：DANGER：演练前必须停写确认，switchover_status 不是 TO STANDBY/TO PRIMARY 时不要强行切；RAC 切换步骤与单机不同。

-- 第 1 步：先确认可切换（只读，主备都查）：
SELECT database_role, switchover_status, open_mode
FROM   v$database;

-- 第 2 步：确认 switchover_status=TO STANDBY / TO PRIMARY 后再执行（DANGER：会切主备角色）：
-- 主库执行：ALTER DATABASE COMMIT TO SWITCHOVER TO PHYSICAL STANDBY;
-- 备库执行：ALTER DATABASE COMMIT TO SWITCHOVER TO PRIMARY;
-- 然后两边分别 SHUTDOWN / STARTUP，按实际演练手册走
