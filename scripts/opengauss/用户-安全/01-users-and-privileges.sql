-- 1. 先查看现有用户与属性（只读）：
SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin, rolvaliduntil FROM pg_roles ORDER BY rolname;
-- 2. 新建用户（模板，密码须符合 openGauss 复杂度要求）：
-- DANGER: CREATE USER <USERNAME> WITH PASSWORD '<PASSWORD>';
-- 3. 授权示例：
-- DANGER: GRANT SELECT ON <SCHEMA>.<TABLE> TO <USERNAME>;
