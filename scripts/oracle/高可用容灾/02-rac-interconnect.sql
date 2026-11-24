-- RAC 互联 / 心跳检查
-- 适用版本：11g+
-- 风险：只读
-- 说明：oifcfg / 集群日志
-- 提醒：互联（private）丢包会触发节点驱逐；is_public='NO' 的才是互联，勿把公网 IP 当互联。

SELECT inst_id, name, ip_address, is_public, source
FROM   gv$cluster_interconnects
ORDER  BY inst_id;

-- Shell（服务器上执行）：
-- oifcfg getif
-- crsctl check cssd
-- crsctl stat res -t
