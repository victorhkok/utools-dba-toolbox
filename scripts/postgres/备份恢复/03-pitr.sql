-- PITR（WAL + recovery_target_time）
-- 适用版本：12+
-- 风险：危险
-- 说明：需连续WAL。PITR 要求归档连续、WAL 不缺；12+ 用 recovery.signal，不再用 recovery.conf。
-- 大类：备份恢复 / 小类：备份

-- 第 1 步：先确认归档和 WAL 连续
SELECT * FROM pg_stat_archiver;
SHOW archive_mode;
SHOW archive_command;
SELECT pg_current_wal_lsn() AS current_wal_lsn;
-- DANGER：PITR 要在新目录恢复，不是在原库直接跑；先停写、备好全备+连续 WAL
-- postgresql.conf: restore_command = 'cp /path/to/archive/%f %p'
-- postgresql.conf: recovery_target_time = '<target_time>'
-- 12+ 不再用 recovery.conf，改用 postgresql.conf + 空文件 recovery.signal
