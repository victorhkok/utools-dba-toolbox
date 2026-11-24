-- 生成 AWR 快照 / 报告
-- 适用版本：11g+
-- 风险：只读
-- 说明：awrrpt.sql，需Diagnostic Pack授权
-- 提醒：AWR 需 Diagnostic Pack 授权，无授权不要用 dba_hist_*；create_snapshot 本身是写操作，虽列为只读条目，执行前确认授权。

-- 1) 查已有快照（近 1 天）：
SELECT snap_id, begin_interval_time, end_interval_time
FROM   dba_hist_snapshot
WHERE  begin_interval_time >= SYSDATE - 1
ORDER  BY snap_id DESC;

-- 2) 手动建一个快照（SQL*Plus / PL/SQL）：
-- EXEC DBMS_WORKLOAD_REPOSITORY.create_snapshot();

-- 3) 生成报告（SQL*Plus，在服务器上执行，选上面查到的起止 snap_id）：
-- @$ORACLE_HOME/rdbms/admin/awrrpt.sql
-- 按提示输入：html/text、起止 snap_id、报告文件名
