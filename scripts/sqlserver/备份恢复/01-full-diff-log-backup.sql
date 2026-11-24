-- 完整 / 差异 / 日志备份
-- 适用版本：2016+
-- 风险：谨慎
-- 说明：BACKUP DATABASE/LOG。日志备份要求数据库是完整/大容量日志恢复模式，简单模式下 BACKUP LOG 会报错。
-- 大类：备份恢复 / 小类：备份

-- 完整备份
BACKUP DATABASE [<db_name>] TO DISK = '<backup_path>.bak' WITH INIT, COMPRESSION;
-- 差异备份
BACKUP DATABASE [<db_name>] TO DISK = '<backup_path>_diff.bak' WITH DIFFERENTIAL, COMPRESSION;
-- 日志备份
BACKUP LOG [<db_name>] TO DISK = '<backup_path>.trn' WITH COMPRESSION;
