-- 1. 列出全部表空间（只读）：
SELECT spcname FROM pg_tablespace;
-- 2. 单个表空间已用字节（只读，单位字节）：
SELECT pg_tablespace_size('<TABLESPACE>') AS size_bytes;
