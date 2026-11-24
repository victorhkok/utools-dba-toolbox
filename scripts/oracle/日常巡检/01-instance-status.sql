-- 实例状态 / 版本 / 启动时间
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$instance, v$database
-- 提醒：v$instance/v$database 均需 SYSDBA 或 SELECT_CATALOG_ROLE 权限；RAC 下每节点各查一次。

SELECT i.instance_name,
       i.host_name,
       i.version,
       i.status,
       i.startup_time,
       d.name        AS db_name,
       d.open_mode,
       d.log_mode
FROM   v$instance i,
       v$database d;
