-- 闪回（binlog2sql）
-- 适用版本：5.7+
-- 风险：危险
-- 说明：DELETE/UPDATE 闪回
-- 大类：备份恢复 / 小类：物理备份
-- shell: python binlog2sql.py -h<host> -u<user> -d<db> -t<table> --start-file="<binlog文件>" --start-datetime="2026-11-24 10:00:00" --stop-datetime="2026-11-24 11:00:00" -B
-- 闪回只对 DML 有效，先确认：
SHOW VARIABLES LIKE 'binlog_format';
