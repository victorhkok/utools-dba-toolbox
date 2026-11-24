-- 主从延迟（Seconds_Behind_Master）
-- 适用版本：5.7+
-- 风险：只读
-- 说明：SHOW SLAVE STATUS
-- 大类：高可用 / 复制 / 小类：主从
-- 5.7: SHOW SLAVE STATUS
-- 8.0+: SHOW REPLICA STATUS（5.7 的 SHOW SLAVE STATUS 在 8.0 仍可用，8.4 已移除）
SHOW SLAVE STATUS;
