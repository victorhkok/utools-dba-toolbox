-- 弱密码 / 无密码账号
-- 适用版本：5.7+
-- 风险：只读
-- 说明：authentication_string 为空
-- 大类：用户 / 安全 / 小类：账号
SELECT User, Host, plugin FROM mysql.user WHERE authentication_string = '' OR authentication_string IS NULL LIMIT 50;
