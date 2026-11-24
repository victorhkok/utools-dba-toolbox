-- 行级安全（RLS）检查
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_policies。RLS 只对表所有者之外的用户生效，超级用户和表所有者默认绕过。
-- 大类：用户 / 安全 / 小类：账号

SELECT schemaname, tablename, rowsecurity AS rls_enabled, relforcerowsecurity
FROM pg_tables
WHERE rowsecurity
ORDER BY schemaname, tablename
LIMIT 20;
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
ORDER BY schemaname, tablename, policyname
LIMIT 20;
