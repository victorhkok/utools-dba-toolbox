-- 1. 先确认归档与备份（只读）：
SHOW archive_mode;
SELECT * FROM sys_stat_archiver;
-- 2. 恢复为危险操作，先停库、先在测试库全流程演练：
-- DANGER: sys_rman restore -D <数据目录> -R <备份仓库目录>
-- DANGER: 恢复后按手册用 WAL 归档做时间点恢复（PITR），切勿在生产库直接演练。
