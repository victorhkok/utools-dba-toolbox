-- 1. 先查看备份记录（只读）：
SHOW BACKUPS;
-- 2. 全量备份（仅企业版，联机执行）：
-- DANGER: CREATE FULL BACKUP ON DNODE <DNODE_ID> TO '<BACKUP_PATH>';
-- 3. 恢复为离线危险操作，先在测试环境演练：
-- DANGER: taosd --restore <BACKUP_CHAIN_PATH> --verify=1
