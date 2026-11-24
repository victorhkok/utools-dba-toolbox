-- 可用性组状态 / 同步延迟
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.dm_hadr_availability_replica_states。同步延迟看 log_send_queue_size 和 redo_queue_size，健康状态看 synchronization_health_desc。
-- 大类：高可用 / 小类：AlwaysOn

SELECT ar.replica_server_name, ars.role_desc,
       ars.availability_mode_desc, ars.synchronization_health_desc,
       ars.last_commit_time,
       DATEDIFF(SECOND, ars.last_commit_time, GETDATE()) AS lag_seconds
FROM sys.dm_hadr_availability_replica_states AS ars
JOIN sys.availability_replicas AS ar
  ON ars.replica_id = ar.replica_id
ORDER BY ars.role_desc;
SELECT TOP 20
       DB_NAME(database_id) AS db_name,
       log_send_queue_size, redo_queue_size, last_commit_time
FROM sys.dm_hadr_database_replica_states
ORDER BY log_send_queue_size DESC;
