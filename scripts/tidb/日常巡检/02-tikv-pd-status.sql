-- TiKV / PD 状态
-- 适用版本：6.x+
-- 风险：只读
-- 说明：pd-ctl / Grafana
-- 备注：TiKV/PD 详细状态以 Dashboard 与 pd-ctl 为准，CLUSTER_INFO 列名需在 TiDB 6.x+ 实测核对。

SELECT TYPE, INSTANCE, STATUS, START_TIME FROM INFORMATION_SCHEMA.CLUSTER_INFO ORDER BY TYPE, INSTANCE LIMIT 20;
-- shell: pd-ctl -u http://<PD_IP>:2379 store
