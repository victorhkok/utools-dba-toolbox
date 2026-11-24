-- 用户 / 权限清单
-- 适用版本：5.7+
-- 风险：只读
-- 说明：mysql.user
-- 大类：用户 / 安全 / 小类：账号
SELECT User, Host FROM mysql.user LIMIT 50;
-- 查某账号权限：SHOW GRANTS FOR '<user>'@'<host>';
