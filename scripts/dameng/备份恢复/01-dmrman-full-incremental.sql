-- 全备 / 增量（BACKUP DATABASE）
-- 适用版本：DM8+
-- 风险：谨慎
-- 说明：DMRMAN
-- 备注：DMRMAN 备份命令语法需按 DM8 版本核对，备份前确认备份目录磁盘余量。

-- shell: DMRMAN（DM8 备份恢复工具，需先停库或按 DMRMAN 要求操作）
-- shell: dmrman CTLFILE=/dm8/data/DAMENG/dm.ini
-- DMRMAN> BACKUP DATABASE '/dm8/data/DAMENG/dm.ini' FULL BACKUPSET '/dm8/backup/full_20261124';
-- DMRMAN> BACKUP DATABASE '/dm8/data/DAMENG/dm.ini' INCREMENTAL BACKUPSET '/dm8/backup/incr_20261124';
