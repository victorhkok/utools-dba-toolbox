-- 复制错误定位（Last_Error）
-- 适用版本：5.7+
-- 风险：只读
-- 说明：IO/SQL线程
-- 大类：高可用 / 复制 / 小类：主从
SHOW SLAVE STATUS;
SELECT SERVICE_STATE, LAST_ERROR_NUMBER, LAST_ERROR_MESSAGE FROM performance_schema.replication_applier_status LIMIT 20;
