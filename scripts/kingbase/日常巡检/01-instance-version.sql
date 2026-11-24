SELECT version() AS version;
SELECT count(*) AS session_count FROM sys_stat_activity;
SELECT state, count(*) AS cnt FROM sys_stat_activity GROUP BY state ORDER BY cnt DESC;
