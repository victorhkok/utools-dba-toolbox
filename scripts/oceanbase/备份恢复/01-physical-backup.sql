-- 物理备份 / 归档（OB 备份）
-- 适用版本：4.x
-- 风险：谨慎
-- 说明：BACKUP DATABASE
-- 备注：OB 物理备份语法与备份目的端配置需在 OB 4.x 实测核对，备份前确认归档已开启。

-- 需先在 OCP / SQL 中配置备份目的端（OSS/NFS 等），再执行：
-- ALTER SYSTEM SET BACKUP_DEST='file:///obbackup';
-- ALTER SYSTEM BACKUP DATABASE;
