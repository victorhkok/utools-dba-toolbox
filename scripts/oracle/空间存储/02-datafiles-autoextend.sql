-- 数据文件 / 自动扩展状态
-- 适用版本：11g+
-- 风险：只读
-- 说明：dba_data_files
-- 提醒：maxbytes=0 表示未设上限或不可扩展，要结合 autoextensible 看；increment_by 单位是块，不是 MB。

SELECT tablespace_name, file_name,
       ROUND(bytes / 1024 / 1024, 2) AS mb,
       ROUND(maxbytes / 1024 / 1024, 2) AS max_mb,
       autoextensible, increment_by
FROM   dba_data_files
ORDER  BY tablespace_name, file_id;
