-- 服务切换 / 负载均衡检查
-- 适用版本：11g+
-- 风险：只读
-- 说明：srvctl config service
-- 提醒：dba_services 看的是数据库内服务定义，实际运行状态以 srvctl status 为准；改服务要 srvctl modify，不要直接改表。

SELECT name, network_name, failover_method, failover_type, failover_retries
FROM   dba_services
ORDER  BY name;

-- Shell（服务器上执行）：
-- srvctl config service -d <db_name>
-- srvctl status service -d <db_name>
