-- 角色 / 权限清单
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_roles。pg_roles 看角色属性，表级授权看 role_table_grants，两者要分开查。
-- 大类：用户 / 安全 / 小类：账号

SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin,
       rolconnlimit, rolvaliduntil
FROM pg_roles
ORDER BY rolname
LIMIT 20;
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
ORDER BY grantee, table_schema, table_name
LIMIT 20;
