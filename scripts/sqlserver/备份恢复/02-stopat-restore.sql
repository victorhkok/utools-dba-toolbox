-- STOPAT 时间点恢复
-- 适用版本：2016+
-- 风险：危险
-- 说明：RESTORE ... STOPAT。STOPAT 恢复要按全备→日志备顺序还原，时间点必须落在日志备份覆盖范围内。
-- 大类：备份恢复 / 小类：备份

-- 第 1 步：先查备份历史，确认全备+日志备的备份集都齐
SELECT TOP 20 database_name, type, backup_start_date, backup_finish_date,
       backup_size / 1024 / 1024 AS backup_size_mb
FROM msdb.dbo.backupset
WHERE database_name = '<db_name>'
ORDER BY backup_finish_date DESC;
-- DANGER：恢复要在测试库/新库验证，先停写，确认 STOPAT 时间点后再取消注释
-- RESTORE DATABASE [<db_name>] FROM DISK = '<full_backup_path>' WITH NORECOVERY;
-- RESTORE LOG [<db_name>] FROM DISK = '<log_backup_path>' WITH STOPAT = '<target_time>', RECOVERY;
