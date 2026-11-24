-- 临时表 / 排序溢出
-- 适用版本：5.7+
-- 风险：只读
-- 说明：Created_tmp_disk_tables
-- 大类：日常巡检 / 小类：健康指标
SHOW GLOBAL STATUS LIKE 'Created_tmp%';
SHOW GLOBAL STATUS LIKE 'Sort_merge_passes';
SHOW GLOBAL STATUS LIKE 'Sort_scan';
SHOW GLOBAL STATUS LIKE 'Sort_range';
