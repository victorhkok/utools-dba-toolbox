-- 审计（8.0 audit log / 5.7 插件）
-- 适用版本：5.7+
-- 风险：只读
-- 说明：按版本区分
-- 大类：用户 / 安全 / 小类：账号
SHOW VARIABLES LIKE 'audit_log%';
SELECT PLUGIN_NAME, PLUGIN_STATUS FROM information_schema.PLUGINS WHERE PLUGIN_NAME = 'audit_log';
