SELECT VERSION() AS db_version;
SHOW GLOBAL STATUS WHERE Variable_name IN ('Uptime', 'Threads_connected', 'Threads_running', 'Queries', 'Slow_queries');
