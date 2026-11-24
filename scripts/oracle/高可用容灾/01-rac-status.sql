-- RAC 节点 / 实例状态
-- 适用版本：11g+
-- 风险：只读
-- 说明：srvctl / crsctl
-- 提醒：gv$instance 需 RAC 环境，单机跑只有一行；crsctl/srvctl 需 grid 用户权限。

-- SQL（gv$instance，各节点一行）：
SELECT inst_id, instance_name, host_name, version, status, startup_time
FROM   gv$instance
ORDER  BY inst_id;

-- Shell（服务器上执行）：
-- crsctl check cluster -all
-- srvctl status database -d <db_name>
-- srvctl status instance -d <db_name> -i <inst_name>
