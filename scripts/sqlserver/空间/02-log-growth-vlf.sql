-- 日志文件增长 / VLF
-- 适用版本：2016+
-- 风险：只读
-- 说明：DBCC LOGINFO。DBCC LOGINFO 看 VLF 数量和状态，VLF 过多会影响日志恢复速度；2017+ 可用 dm_db_log_info。
-- 大类：空间 / 小类：空间

SELECT name AS file_name, type_desc, size * 8 / 1024 AS size_mb,
       growth, is_percent_growth
FROM sys.database_files
WHERE type_desc = 'LOG';
DBCC LOGINFO;
-- 2017+ 也可用：SELECT * FROM sys.dm_db_log_info(DB_ID());
