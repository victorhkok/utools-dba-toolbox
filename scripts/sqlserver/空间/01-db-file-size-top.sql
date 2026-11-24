-- 数据库 / 文件大小 Top
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.database_files。sys.master_files 看所有库，sys.database_files 只看当前库，size 单位是 8KB 页。
-- 大类：空间 / 小类：空间

SELECT TOP 20
       DB_NAME(database_id) AS db_name, name AS file_name,
       type_desc, size * 8 / 1024 AS size_mb,
       max_size * 8 / 1024 AS max_size_mb
FROM sys.master_files
ORDER BY size DESC;
SELECT TOP 20
       name AS file_name, type_desc, size * 8 / 1024 AS size_mb,
       growth, is_percent_growth
FROM sys.database_files
ORDER BY size DESC;
