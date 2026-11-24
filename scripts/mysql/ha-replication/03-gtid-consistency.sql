-- GTID 一致性检查
-- 适用版本：5.7+
-- 风险：只读
-- 说明：gtid_executed
-- 大类：高可用 / 复制 / 小类：主从
SHOW VARIABLES LIKE 'gtid_mode';
SHOW VARIABLES LIKE 'enforce_gtid_consistency';
SELECT @@GLOBAL.gtid_executed AS gtid_executed;
SELECT @@GLOBAL.gtid_purged AS gtid_purged;
