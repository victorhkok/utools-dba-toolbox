-- 备份历史检查
-- 适用版本：2016+
-- 风险：只读
-- 说明：msdb.dbo.backupset。type D=完整、I=差异、L=日志，恢复前先确认最近一次全备和日志备的时间。
-- 大类：备份恢复 / 小类：备份

SELECT TOP 20
       bs.database_name, bs.type, bs.backup_start_date, bs.backup_finish_date,
       bs.backup_size / 1024 / 1024 AS backup_size_mb,
       bmf.physical_device_name
FROM msdb.dbo.backupset AS bs
JOIN msdb.dbo.backupmediafamily AS bmf
  ON bs.media_set_id = bmf.media_set_id
ORDER BY bs.backup_finish_date DESC;
