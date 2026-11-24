-- 主备切换演练
-- 适用版本：4.x
-- 风险：危险
-- 说明：切换前确认
-- 备注：OB 主备切换与 Oracle DG 完全不同，命令需在 OB 4.x 实测核对，演练前务必停写确认。

-- 1. 先确认主备租户与日志同步（只读）：
SELECT TENANT_ID, LS_ID, SVR_IP, ROLE FROM oceanbase.__all_ls ORDER BY TENANT_ID LIMIT 20;
-- 2. 切换为危险操作，演练前停写确认：
-- DANGER: 切换命令按 OB 4.x 主备租户方案执行（OCP 切换或 ALTER SYSTEM 切换），不要直接套用 Oracle DG 命令。
