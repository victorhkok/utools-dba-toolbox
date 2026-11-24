-- 登录名 / 用户 / 角色
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.server_principals。server_principals 是服务器登录名，database_principals 是库内用户，两者要分开查。
-- 大类：用户 / 安全 / 小类：账号

SELECT TOP 20 name, type_desc, is_disabled, create_date
FROM sys.server_principals
WHERE type IN ('S', 'U', 'G')
ORDER BY name;
SELECT TOP 20
       dp.name AS user_name, dp.type_desc,
       dr.name AS role_name
FROM sys.database_principals AS dp
LEFT JOIN sys.database_role_members AS drm
  ON drm.member_principal_id = dp.principal_id
LEFT JOIN sys.database_principals AS dr
  ON dr.principal_id = drm.role_principal_id
ORDER BY dp.name, dr.name;
