-- binlog PITR 恢复
-- 适用版本：5.7+
-- 风险：危险
-- 说明：mysqlbinlog + STOPAT
-- 大类：备份恢复 / 小类：逻辑备份
-- DANGER: 时间点恢复会回放 binlog，先在测试库演练，确认起止时间后再在目标库执行。
-- shell: mysqlbinlog --start-datetime="2026-11-24 10:00:00" --stop-datetime="2026-11-24 11:00:00" "<binlog文件>" | mysql -u <user> -p
-- 先确认 binlog 列表：
SHOW BINARY LOGS;
