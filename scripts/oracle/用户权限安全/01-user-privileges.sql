-- 用户 / 角色 / 权限清单
-- 适用版本：11g+
-- 风险：只读
-- 说明：dba_users / dba_role_privs
-- 提醒：dba_users/dba_role_privs/dba_sys_privs 均需 DBA 权限；查单个用户时把 <username> 换成大写用户名。

SELECT username, account_status, default_tablespace, temporary_tablespace, profile, created
FROM   dba_users
ORDER  BY username;

SELECT grantee, granted_role, admin_option
FROM   dba_role_privs
WHERE  grantee = '<username>'
ORDER  BY granted_role;

SELECT grantee, privilege, admin_option
FROM   dba_sys_privs
WHERE  grantee = '<username>'
ORDER  BY privilege;
