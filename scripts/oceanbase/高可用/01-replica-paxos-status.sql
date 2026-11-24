-- 多副本 / Paxos 状态
-- 适用版本：4.x
-- 风险：只读
-- 说明：__all_ls
-- 备注：__all_ls 的列名需在 OB 4.x 实测核对，副本角色以 OCP 展示为准。

SELECT LS_ID, TENANT_ID, SVR_IP, ROLE, STATUS FROM oceanbase.__all_ls ORDER BY TENANT_ID, LS_ID LIMIT 20;
