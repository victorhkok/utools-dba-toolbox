-- 监听与服务状态
-- 适用版本：11g+
-- 风险：只读
-- 说明：lsnrctl status / srvctl status
-- 提醒：lsnrctl/srvctl 需在服务器 OS 执行，SQL*Plus 里跑不了；先确认 ORACLE_HOME/ORACLE_SID。

-- Shell / OS 命令（非 SQL，在数据库服务器上执行）：
-- lsnrctl status
-- srvctl status database -d <db_name>
-- srvctl status listener
-- crsctl check cluster -all        -- RAC 环境才有
-- 另查数据库内注册的服务：
SELECT name, network_name, failover_method
FROM   dba_services
ORDER  BY name;
