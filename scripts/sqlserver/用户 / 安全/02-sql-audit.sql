-- 审计（SQL Audit）
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.server_audits。server_audits 看审计定义，dm_server_audit_status 看审计当前是否在运行。
-- 大类：用户 / 安全 / 小类：账号

SELECT name, is_state_enabled, type_desc, create_date
FROM sys.server_audits
ORDER BY name;
SELECT audit_id, name, status_desc, status_time
FROM sys.dm_server_audit_status;
