-- 版本 / uptime / 连接数
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_stat_activity。version() 和 pg_postmaster_start_time() 在所有 12+ 版本都有，连接数含后台进程。
-- 大类：日常巡检 / 小类：实例

SELECT version() AS pg_version;
SELECT pg_postmaster_start_time() AS start_time,
       now() - pg_postmaster_start_time() AS uptime;
SELECT count(*) AS total_connections,
       count(*) FILTER (WHERE state = 'active') AS active_connections
FROM pg_stat_activity;
