-- 集群 / 租户 / Zone 状态
-- 适用版本：4.x
-- 风险：只读
-- 说明：__all_server / __all_tenant
-- 备注：MySQL 模式用以上查询，Oracle 模式需改写为对应字典视图，需在 OB 4.x 实测核对。

SELECT SVR_IP, SVR_PORT, ZONE, STATUS FROM oceanbase.__all_server ORDER BY ZONE, SVR_IP LIMIT 20;
SELECT TENANT_ID, TENANT_NAME, CREATE_TIME FROM oceanbase.__all_tenant LIMIT 20;
