-- 恢复演练清单（只读检查 + 演练步骤，恢复命令以官方手册为准，禁止凭印象执行）：
-- 1. 确认归档模式（只读）：
SELECT DATABASE_NAME, LOG_MODE, OPEN_MODE FROM V$DATABASE;
-- 2. 确认归档连续性（只读）：
SELECT SEQUENCE#, FIRST_TIME FROM V$ARCHIVED_LOG WHERE FIRST_TIME > SYSDATE - 7 ORDER BY SEQUENCE#;
-- 3. 确认最近备份集可用（按管理员手册的备份集管理方式核对）；
-- DANGER: 恢复命令（工具名与参数）需按 YashanDB 管理员手册核对，先在测试库全流程演练，生产恢复前先停写并做副本。
