-- 故障转移演练清单
-- 适用版本：2016+
-- 风险：危险
-- 说明：AG Failover。手动故障转移要求目标副本同步且健康，异步副本切换可能丢数据。
-- 大类：高可用 / 小类：AlwaysOn

-- 第 1 步：先查可用性组状态，确认目标副本已同步、健康
SELECT ar.replica_server_name, ars.role_desc, ars.synchronization_health_desc
FROM sys.dm_hadr_availability_replica_states AS ars
JOIN sys.availability_replicas AS ar
  ON ars.replica_id = ar.replica_id;
-- DANGER：只在演练窗口、确认业务可停写后执行，生产切换前先在测试环境演练
-- ALTER AVAILABILITY GROUP [<ag_name>] FAILOVER;
