-- 表空间使用率 Top
-- 适用版本：11g+
-- 风险：只读
-- 说明：>85%预警
-- 提醒：使用率 >85% 预警，>95% 立即处理；临时表空间不在 dba_data_files 里，见“临时表空间使用”那条。

SELECT df.tablespace_name,
       ROUND(df.total_mb, 2)                         AS total_mb,
       ROUND(NVL(fs.free_mb, 0), 2)                 AS free_mb,
       ROUND((df.total_mb - NVL(fs.free_mb, 0)) / df.total_mb * 100, 2) AS pct_used
FROM   (SELECT tablespace_name, SUM(bytes) / 1024 / 1024 AS total_mb
        FROM   dba_data_files
        GROUP  BY tablespace_name) df
       LEFT JOIN
       (SELECT tablespace_name, SUM(bytes) / 1024 / 1024 AS free_mb
        FROM   dba_free_space
        GROUP  BY tablespace_name) fs
       ON df.tablespace_name = fs.tablespace_name
ORDER  BY pct_used DESC;
