-- 版本 / 实例状态
-- 适用版本：2016+
-- 风险：只读
-- 说明：@@VERSION / sys.dm_os_sys_info。@@VERSION 看版本，sys.dm_os_sys_info 看 CPU/内存和启动时间。
-- 大类：日常巡检 / 小类：实例

SELECT @@VERSION AS version;
SELECT SERVERPROPERTY('Edition') AS edition,
       SERVERPROPERTY('ProductVersion') AS product_version,
       SERVERPROPERTY('ProductLevel') AS product_level;
SELECT cpu_count, physical_memory_kb / 1024 / 1024 AS physical_memory_gb,
       sqlserver_start_time, virtual_machine_type_desc
FROM sys.dm_os_sys_info;
