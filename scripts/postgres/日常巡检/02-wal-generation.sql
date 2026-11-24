-- WAL 生成量
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_stat_wal。pg_stat_wal 仅 14+ 有，12/13 查 pg_stat_archiver + pg_current_wal_lsn()。
-- 大类：日常巡检 / 小类：实例

-- PG 14+ 首选 pg_stat_wal；12/13 没有该视图，用下面两条代替
SELECT * FROM pg_stat_archiver;
SELECT pg_current_wal_lsn() AS current_wal_lsn,
       pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS wal_bytes_since_start;
-- PG 14+ 可另跑：SELECT wal_records, wal_bytes, wal_write_time FROM pg_stat_wal;
