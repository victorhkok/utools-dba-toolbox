-- 表空间扩容（ADD DATAFILE）
-- 适用版本：11g+
-- 风险：危险
-- 说明：先查磁盘余量
-- 提醒：DANGER：先确认磁盘余量和文件路径权限；SIZE/MAXSIZE 按实际剩余空间填，不要照抄 1G/UNLIMITED。

-- 第 1 步：先查表空间和磁盘（只读）：
SELECT tablespace_name, file_name,
       ROUND(bytes / 1024 / 1024, 2) AS mb,
       autoextensible,
       ROUND(maxbytes / 1024 / 1024, 2) AS max_mb
FROM   dba_data_files
WHERE  tablespace_name = '<tablespace_name>'
ORDER  BY file_id;

-- 第 2 步：确认磁盘余量（Shell：df -h <datafile_dir>），确认后再执行（DANGER）：
-- ALTER TABLESPACE <tablespace_name> ADD DATAFILE '<datafile_path>' SIZE 1G AUTOEXTEND ON NEXT 100M MAXSIZE UNLIMITED;
