-- 缓存命中率 / 内存使用
-- 适用版本：2016+
-- 风险：只读
-- 说明：sys.dm_os_performance_counters。Buffer cache hit ratio 要除以同名的 base 计数器再乘 100，单看 cntr_value 不准。
-- 大类：性能优化 / 小类：DMV

SELECT object_name, counter_name, cntr_value
FROM sys.dm_os_performance_counters
WHERE counter_name IN ('Buffer cache hit ratio',
                       'Buffer cache hit ratio base',
                       'Page life expectancy',
                       'Total Server Memory (KB)',
                       'Target Server Memory (KB)')
ORDER BY object_name, counter_name;
SELECT physical_memory_kb / 1024 AS physical_memory_mb,
       virtual_memory_kb / 1024 AS virtual_memory_mb
FROM sys.dm_os_sys_info;
