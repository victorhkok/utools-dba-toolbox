#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill PG (26) + SQL Server (20) SQL. Titles/versions/risk copied verbatim from toolbox.json.
Writes data/toolbox-postgres.json, data/toolbox-sqlserver.json and scripts/<db>/<大类>/NN-slug.sql
NN resets per subcategory (小类内序号).
"""
import json, pathlib, re, copy
ROOT = pathlib.Path(__file__).parent
SRC = json.load(open(ROOT/'data'/'toolbox.json', encoding='utf-8'))
DBS = {d['id']: d for d in SRC['databases']}

# (slug, sql, params, notes) keyed by (db_id, title)
# PG
PG = {
"版本 / uptime / 连接数": ("version-uptime-connections",
"""SELECT version() AS pg_version;
SELECT pg_postmaster_start_time() AS start_time,
       now() - pg_postmaster_start_time() AS uptime;
SELECT count(*) AS total_connections,
       count(*) FILTER (WHERE state = 'active') AS active_connections
FROM pg_stat_activity;""",
[], "version() 和 pg_postmaster_start_time() 在所有 12+ 版本都有，连接数含后台进程。"),
"WAL 生成量": ("wal-generation",
"""-- PG 14+ 首选 pg_stat_wal；12/13 没有该视图，用下面两条代替
SELECT * FROM pg_stat_archiver;
SELECT pg_current_wal_lsn() AS current_wal_lsn,
       pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS wal_bytes_since_start;
-- PG 14+ 可另跑：SELECT wal_records, wal_bytes, wal_write_time FROM pg_stat_wal;""",
[], "pg_stat_wal 仅 14+ 有，12/13 查 pg_stat_archiver + pg_current_wal_lsn()。"),
"后台进程状态": ("backend-processes",
"""SELECT backend_type, state, count(*) AS cnt
FROM pg_stat_activity
GROUP BY backend_type, state
ORDER BY cnt DESC
LIMIT 20;
SELECT pid, backend_type, state, now() - query_start AS duration, left(query, 200) AS query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start
LIMIT 20;""",
[], "backend_type 区分 autovacuum / walsender / checkpointer 等后台进程。"),
"shared_buffers / work_mem 建议": ("shared-buffers-work-mem",
"""SELECT name, setting, unit, context, short_desc
FROM pg_settings
WHERE name IN ('shared_buffers','work_mem','maintenance_work_mem',
               'effective_cache_size','max_connections')
ORDER BY name;
SHOW shared_buffers;
SHOW work_mem;""",
[], "只读查询参数，不改配置；调参要结合内存总量和连接数，改完需 reload/重启看 context。"),
"缓存命中率（heap / index）": ("cache-hit-ratio",
"""SELECT schemaname, relname,
       heap_blks_read, heap_blks_hit,
       round(100.0 * heap_blks_hit / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS heap_hit_pct,
       idx_blks_read, idx_blks_hit,
       round(100.0 * idx_blks_hit / NULLIF(idx_blks_hit + idx_blks_read, 0), 2) AS idx_hit_pct
FROM pg_statio_user_tables
ORDER BY heap_blks_read DESC
LIMIT 20;""",
[], "heap 命中率低于 99% 且读盘大时先看 shared_buffers 和热点表。"),
"统计信息 / ANALYZE 状态": ("analyze-status",
"""SELECT schemaname, relname, n_live_tup, n_mod_since_analyze,
       last_analyze, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_mod_since_analyze DESC NULLS LAST
LIMIT 20;""",
[], "n_mod_since_analyze 大且 last_analyze 很旧，说明统计信息过期。"),
"自动 VACUUM 状态": ("autovacuum-status",
"""SELECT name, setting, unit
FROM pg_settings
WHERE name LIKE 'autovacuum%'
ORDER BY name;
SELECT schemaname, relname, last_autovacuum, last_autoanalyze,
       autovacuum_count, autoanalyze_count
FROM pg_stat_user_tables
ORDER BY last_autovacuum NULLS FIRST
LIMIT 20;""",
[], "autovacuum 关了或 long-running 事务堵住时，死元组会一直涨。"),
"未使用索引": ("unused-indexes",
"""SELECT schemaname, relname AS table_name, indexrelname AS index_name,
       idx_scan, pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE 'pg_%'
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;""",
[], "idx_scan=0 只说明统计周期内没用过，删前确认统计周期够长且不是唯一约束索引。"),
"缺失索引（hypopg 评估）": ("missing-index-hypopg",
"""-- 先确认扩展：hypopg 不在 PG 核心里，需先安装
SELECT * FROM pg_extension WHERE extname = 'hypopg';
-- 模板：用参数替换表名和列名，只做假设评估，不会真建索引
-- SELECT * FROM hypopg_create_index('CREATE INDEX ON <table_name> (<column_list>)');
-- SELECT * FROM hypopg_list_indexes();
-- 评估完清理：SELECT * FROM hypopg_drop_index(<hypopg_index_oid>);
-- 再用 EXPLAIN 对比加假设索引前后的计划""",
["table_name","column_list"], "hypopg 是第三方扩展，需先 CREATE EXTENSION hypopg；它只做假设，不建真实索引。"),
"膨胀索引 / bloat 评估": ("index-bloat",
"""-- 先确认扩展：pgstattuple 不在 PG 核心里
SELECT * FROM pg_extension WHERE extname = 'pgstattuple';
-- 单个索引评估（替换参数为索引名）：
-- SELECT * FROM pgstatindex('<index_name>');
-- 无扩展时的替代：只看索引大小排序，再结合表膨胀判断
SELECT schemaname, relname AS table_name, indexrelname AS index_name,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;""",
["index_name"], "pgstatindex 一次只能查一个索引，全库 bloat 需循环或用 pgstattuple 的近似估算查询。"),
"pg_stat_statements Top SQL": ("pg-stat-statements-top",
"""-- 前置（一次）：CREATE EXTENSION pg_stat_statements;
-- PG 13+ 用 total_exec_time / mean_exec_time；PG 12 用 total_time / mean_time
SELECT query, calls,
       round(total_exec_time::numeric, 2) AS total_exec_time_ms,
       round(mean_exec_time::numeric, 2) AS mean_exec_time_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;""",
[], "需先 CREATE EXTENSION pg_stat_statements 并在 shared_preload_libraries 里加载，PG 12 列名是 total_time/mean_time。"),
"慢查询日志（log_min_duration）": ("slow-query-log-settings",
"""SELECT name, setting, unit, context
FROM pg_settings
WHERE name IN ('log_min_duration_statement','log_statement',
               'log_directory','logging_collector','log_filename')
ORDER BY name;
-- 改阈值模板（改完 pg_reload_conf() 即可，不用重启）：
-- ALTER SYSTEM SET log_min_duration_statement = '1000';
-- SELECT pg_reload_conf();""",
[], "log_min_duration_statement 单位是毫秒，设 1000 即只记 >1s 的；改配置用 ALTER SYSTEM + reload。"),
"EXPLAIN ANALYZE": ("explain-analyze",
"""-- 把 <query_text> 换成要分析的 SQL；真实执行，会跑完查询
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <query_text>;""",
["query_text"], "EXPLAIN ANALYZE 会真实执行，大查询/写操作先在测试库跑，别在生产直接跑。"),
"阻塞锁链（pg_blocking_pids）": ("blocking-chain",
"""SELECT blocked.pid AS blocked_pid, blocked.usename AS blocked_user,
       blocked.application_name, blocked.state,
       now() - blocked.query_start AS blocked_duration,
       blocking.pid AS blocking_pid, blocking.usename AS blocking_user,
       left(blocked.query, 200) AS blocked_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking
  ON blocking.pid = ANY (pg_blocking_pids(blocked.pid))
WHERE cardinality(pg_blocking_pids(blocked.pid)) > 0
ORDER BY blocked_duration DESC
LIMIT 20;""",
[], "pg_blocking_pids() 返回阻塞该会话的 pid 数组，根因一般是排头的 blocking_pid。"),
"死锁统计": ("deadlock-stats",
"""SELECT datname, deadlocks, stats_reset
FROM pg_stat_database
ORDER BY deadlocks DESC
LIMIT 20;""",
[], "pg_stat_database 只有死锁次数，没有死锁明细，明细要去日志里找 deadlock detected。"),
"终止会话（pg_terminate_backend）": ("terminate-session",
"""-- 第 1 步：先确认要杀的会话（长运行活跃会话）
SELECT pid, usename, application_name, client_addr, state,
       now() - query_start AS duration, left(query, 200) AS query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '5 minutes'
ORDER BY duration DESC
LIMIT 20;
-- DANGER：确认 pid 无误后再取消注释执行，杀错会话会中断业务
-- SELECT pg_terminate_backend(<pid>);""",
["pid"], "先查清 pid、用户和 SQL 再杀；pg_terminate_backend 会直接断开该连接。"),
"库 / 表大小 Top": ("db-table-size-top",
"""SELECT datname, pg_size_pretty(pg_database_size(datname)) AS db_size
FROM pg_database
ORDER BY pg_database_size(datname) DESC
LIMIT 20;
SELECT schemaname, relname,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
       pg_size_pretty(pg_relation_size(relid)) AS table_size,
       pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;""",
[], "pg_total_relation_size 含表+索引+TOAST，单看表大小用 pg_relation_size。"),
"表膨胀 / VACUUM 建议": ("table-bloat-vacuum",
"""-- 第 1 步：先看死元组和上次 VACUUM
SELECT schemaname, relname, n_live_tup, n_dead_tup,
       last_vacuum, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;
-- 普通 VACUUM 不锁表，可在线跑（替换表名）：
-- VACUUM (VERBOSE, ANALYZE) <schema_name>.<table_name>;
-- DANGER：VACUUM FULL 会重写整张表、独占锁、需额外磁盘空间，非高峰+确认后再跑
-- VACUUM FULL <schema_name>.<table_name>;""",
["schema_name","table_name"], "VACUUM 不锁表，VACUUM FULL 会独占锁并重写表，两者不要混用。"),
"死元组比例": ("dead-tuple-ratio",
"""SELECT schemaname, relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
       last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;""",
[], "死元组占比高且 autovacuum 没跟上时，先查长事务是否堵住了 VACUUM。"),
"pg_dump / pg_dumpall": ("pg-dump",
"""-- shell: pg_dump -h <host> -U <user> -d <db_name> -F c -f <backup_path>.dump
-- shell: pg_dump -h <host> -U <user> -d <db_name> -F p -f <backup_path>.sql
-- shell: pg_dumpall -h <host> -U <user> -f <backup_path>-globals.sql
-- shell: pg_dump --version""",
["host","user","db_name","backup_path"], "pg_dump 是逻辑备份，大库慢；-F c 是自定义格式，恢复用 pg_restore。"),
"pg_basebackup 物理备份": ("pg-basebackup",
"""-- shell: pg_basebackup -h <host> -U <replicator_user> -D <backup_dir> -Ft -z -P -v -X stream
-- shell: pg_basebackup -h <host> -U <replicator_user> -D <backup_dir> -Fp -P -v -X stream""",
["host","replicator_user","backup_dir"], "pg_basebackup 需复制账号有 REPLICATION 权限，-X stream 才会把 WAL 一起备走。"),
"PITR（WAL + recovery_target_time）": ("pitr",
"""-- 第 1 步：先确认归档和 WAL 连续
SELECT * FROM pg_stat_archiver;
SHOW archive_mode;
SHOW archive_command;
SELECT pg_current_wal_lsn() AS current_wal_lsn;
-- DANGER：PITR 要在新目录恢复，不是在原库直接跑；先停写、备好全备+连续 WAL
-- postgresql.conf: restore_command = 'cp /path/to/archive/%f %p'
-- postgresql.conf: recovery_target_time = '<target_time>'
-- 12+ 不再用 recovery.conf，改用 postgresql.conf + 空文件 recovery.signal""",
["target_time"], "PITR 要求归档连续、WAL 不缺；12+ 用 recovery.signal，不再用 recovery.conf。"),
"主从延迟（pg_stat_replication）": ("replication-lag",
"""SELECT application_name, client_addr, state, sync_state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag_bytes,
       replay_lag, write_lag, flush_lag
FROM pg_stat_replication
ORDER BY replay_lag DESC
LIMIT 20;""",
[], "replay_lag 是备库回放延迟，write/flush 延迟大而 replay 小时说明回放跟不上。"),
"同步 / 异步模式检查": ("sync-async-mode",
"""SHOW synchronous_standby_names;
SHOW synchronous_commit;
SELECT application_name, sync_state, state
FROM pg_stat_replication
ORDER BY application_name
LIMIT 20;""",
[], "synchronous_standby_names 为空即异步；同步模式下主库提交要等备库确认。"),
"角色 / 权限清单": ("roles-permissions",
"""SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin,
       rolconnlimit, rolvaliduntil
FROM pg_roles
ORDER BY rolname
LIMIT 20;
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
ORDER BY grantee, table_schema, table_name
LIMIT 20;""",
[], "pg_roles 看角色属性，表级授权看 role_table_grants，两者要分开查。"),
"行级安全（RLS）检查": ("row-level-security",
"""SELECT schemaname, tablename, rowsecurity AS rls_enabled, relforcerowsecurity
FROM pg_tables
WHERE rowsecurity
ORDER BY schemaname, tablename
LIMIT 20;
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
ORDER BY schemaname, tablename, policyname
LIMIT 20;""",
[], "RLS 只对表所有者之外的用户生效，超级用户和表所有者默认绕过。"),
}

SS = {
"版本 / 实例状态": ("version-instance-status",
"""SELECT @@VERSION AS version;
SELECT SERVERPROPERTY('Edition') AS edition,
       SERVERPROPERTY('ProductVersion') AS product_version,
       SERVERPROPERTY('ProductLevel') AS product_level;
SELECT cpu_count, physical_memory_kb / 1024 / 1024 AS physical_memory_gb,
       sqlserver_start_time, virtual_machine_type_desc
FROM sys.dm_os_sys_info;""",
[], "@@VERSION 看版本，sys.dm_os_sys_info 看 CPU/内存和启动时间。"),
"连接 / 作业（Agent Job）状态": ("connections-agent-jobs",
"""SELECT login_name, host_name, program_name, count(*) AS session_count
FROM sys.dm_exec_sessions
WHERE is_user_process = 1
GROUP BY login_name, host_name, program_name
ORDER BY session_count DESC;
SELECT TOP 20 j.name AS job_name, j.enabled,
       ja.run_requested_date, ja.stop_execution_date
FROM msdb.dbo.sysjobs AS j
LEFT JOIN msdb.dbo.sysjobactivity AS ja
  ON ja.job_id = j.job_id
ORDER BY j.name;""",
[], "sys.dm_exec_sessions 只看用户会话，作业状态在 msdb 的 sysjobs/sysjobactivity。"),
"缓存命中率 / 内存使用": ("cache-hit-ratio-memory",
"""SELECT object_name, counter_name, cntr_value
FROM sys.dm_os_performance_counters
WHERE counter_name IN ('Buffer cache hit ratio',
                       'Buffer cache hit ratio base',
                       'Page life expectancy',
                       'Total Server Memory (KB)',
                       'Target Server Memory (KB)')
ORDER BY object_name, counter_name;
SELECT physical_memory_kb / 1024 AS physical_memory_mb,
       virtual_memory_kb / 1024 AS virtual_memory_mb
FROM sys.dm_os_sys_info;""",
[], "Buffer cache hit ratio 要除以同名的 base 计数器再乘 100，单看 cntr_value 不准。"),
"缺失索引 DMV": ("missing-indexes-dmv",
"""SELECT TOP 20
       migs.avg_total_user_cost * migs.avg_user_impact
         * (migs.user_seeks + migs.user_scans) AS improvement_measure,
       mid.statement AS table_name,
       mid.equality_columns, mid.inequality_columns, mid.included_columns
FROM sys.dm_db_missing_index_groups AS mig
INNER JOIN sys.dm_db_missing_index_group_stats AS migs
  ON migs.group_handle = mig.index_group_handle
INNER JOIN sys.dm_db_missing_index_details AS mid
  ON mig.index_handle = mid.index_handle
ORDER BY improvement_measure DESC;""",
[], "DMV 只给建议，建索引前要核对表大小、写比例和已有索引，避免重复建。"),
"统计信息过期": ("stale-statistics",
"""SELECT TOP 20
       OBJECT_NAME(s.object_id) AS table_name,
       s.name AS stats_name, s.auto_created, s.user_created,
       STATS_DATE(s.object_id, s.stats_id) AS last_updated,
       p.modification_counter, p.rows, p.rows_sampled
FROM sys.stats AS s
CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) AS p
ORDER BY last_updated ASC;""",
[], "modification_counter 大且 last_updated 很旧，说明统计信息过期，UPDATE STATISTICS 前先评估。"),
"Query Store Top SQL（2016+）": ("query-store-top-sql",
"""-- 前置：Query Store 需开启，查 sys.database_query_store_options 确认
SELECT state_desc FROM sys.database_query_store_options;
SELECT TOP 20
       q.query_id,
       LEFT(qt.query_sql_text, 200) AS query_text,
       rs.avg_duration AS avg_duration_us,
       rs.count_executions,
       rs.avg_cpu_time, rs.avg_logical_io_reads
FROM sys.query_store_query AS q
JOIN sys.query_store_query_text AS qt
  ON qt.query_text_id = q.query_text_id
JOIN sys.query_store_plan AS p
  ON p.query_id = q.query_id
JOIN sys.query_store_runtime_stats AS rs
  ON rs.plan_id = p.plan_id
ORDER BY rs.avg_duration DESC;""",
[], "Query Store 需先开启（ALTER DATABASE SET QUERY_STORE = ON），没开时这些视图是空的。"),
"最耗 CPU / IO 的查询": ("top-cpu-io-queries",
"""SELECT TOP 20
       qs.total_worker_time / 1000 AS total_cpu_ms,
       qs.total_logical_reads, qs.total_logical_writes,
       qs.execution_count,
       SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1,
         ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(st.text)
           ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) + 1) AS query_text
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY qs.total_worker_time DESC;""",
[], "dm_exec_query_stats 是缓存累计值，重启/缓存清理后会清零，对比要看 execution_count。"),
"执行计划（实际 vs 预估）": ("execution-plan-actual-vs-estimated",
"""SELECT TOP 20
       qs.plan_handle, qs.execution_count,
       SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1,
         ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(st.text)
           ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) + 1) AS query_text
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY qs.execution_count DESC;
-- 取某条计划的 XML（替换参数为 plan_handle 的二进制值，需在 SSMS 里转）：
-- SELECT query_plan FROM sys.dm_exec_query_plan(<plan_handle>);
-- 实际执行计划在 SSMS 里用 Ctrl+M 开“包括实际执行计划”再跑查询""",
["plan_handle"], "DMV 给的是缓存的预估计划，真实执行耗时要看 SSMS 的实际执行计划。"),
"阻塞链（sys.dm_exec_requests）": ("blocking-chain",
"""SELECT TOP 20
       r.session_id, r.blocking_session_id, r.wait_type, r.wait_time,
       r.status, r.command,
       SUBSTRING(t.text, (r.statement_start_offset / 2) + 1,
         ((CASE r.statement_end_offset WHEN -1 THEN DATALENGTH(t.text)
           ELSE r.statement_end_offset END - r.statement_start_offset) / 2) + 1) AS query_text
FROM sys.dm_exec_requests AS r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) AS t
WHERE r.blocking_session_id <> 0
ORDER BY r.wait_time DESC;""",
[], "blocking_session_id 是直接阻塞者，链的根因要顺着 blocking_session_id 往上追。"),
"死锁图（Extended Events）": ("deadlock-graph-xe",
"""SELECT CAST(xet.target_data AS XML) AS xe_data
FROM sys.dm_xe_session_targets AS xet
JOIN sys.dm_xe_sessions AS xe
  ON xe.address = xet.event_session_address
WHERE xe.name = 'system_health'
  AND xet.target_name = 'ring_buffer';
-- 在返回的 XML 里找 xml_deadlock_report 事件；也可以在 SSMS 的扩展事件里直接看 system_health""",
[], "死锁图在 system_health 会话的 ring_buffer 里，XML 需解析 xml_deadlock_report 事件。"),
"KILL 会话": ("kill-session",
"""-- 第 1 步：先确认要杀的会话
SELECT session_id, login_name, host_name, program_name, status, command,
       cpu_time, reads, writes
FROM sys.dm_exec_sessions
WHERE session_id = <spid>;
-- DANGER：确认 spid 无误后再取消注释执行，KILL 会回滚该会话的事务
-- KILL <spid>;""",
["spid"], "KILL 前先确认 spid、登录名和正在跑的命令，杀掉后事务要回滚。"),
"数据库 / 文件大小 Top": ("db-file-size-top",
"""SELECT TOP 20
       DB_NAME(database_id) AS db_name, name AS file_name,
       type_desc, size * 8 / 1024 AS size_mb,
       max_size * 8 / 1024 AS max_size_mb
FROM sys.master_files
ORDER BY size DESC;
SELECT TOP 20
       name AS file_name, type_desc, size * 8 / 1024 AS size_mb,
       growth, is_percent_growth
FROM sys.database_files
ORDER BY size DESC;""",
[], "sys.master_files 看所有库，sys.database_files 只看当前库，size 单位是 8KB 页。"),
"日志文件增长 / VLF": ("log-growth-vlf",
"""SELECT name AS file_name, type_desc, size * 8 / 1024 AS size_mb,
       growth, is_percent_growth
FROM sys.database_files
WHERE type_desc = 'LOG';
DBCC LOGINFO;
-- 2017+ 也可用：SELECT * FROM sys.dm_db_log_info(DB_ID());""",
[], "DBCC LOGINFO 看 VLF 数量和状态，VLF 过多会影响日志恢复速度；2017+ 可用 dm_db_log_info。"),
"完整 / 差异 / 日志备份": ("full-diff-log-backup",
"""-- 完整备份
BACKUP DATABASE [<db_name>] TO DISK = '<backup_path>.bak' WITH INIT, COMPRESSION;
-- 差异备份
BACKUP DATABASE [<db_name>] TO DISK = '<backup_path>_diff.bak' WITH DIFFERENTIAL, COMPRESSION;
-- 日志备份
BACKUP LOG [<db_name>] TO DISK = '<backup_path>.trn' WITH COMPRESSION;""",
["db_name","backup_path"], "日志备份要求数据库是完整/大容量日志恢复模式，简单模式下 BACKUP LOG 会报错。"),
"STOPAT 时间点恢复": ("stopat-restore",
"""-- 第 1 步：先查备份历史，确认全备+日志备的备份集都齐
SELECT TOP 20 database_name, type, backup_start_date, backup_finish_date,
       backup_size / 1024 / 1024 AS backup_size_mb
FROM msdb.dbo.backupset
WHERE database_name = '<db_name>'
ORDER BY backup_finish_date DESC;
-- DANGER：恢复要在测试库/新库验证，先停写，确认 STOPAT 时间点后再取消注释
-- RESTORE DATABASE [<db_name>] FROM DISK = '<full_backup_path>' WITH NORECOVERY;
-- RESTORE LOG [<db_name>] FROM DISK = '<log_backup_path>' WITH STOPAT = '<target_time>', RECOVERY;""",
["db_name","target_time","full_backup_path","log_backup_path"], "STOPAT 恢复要按全备→日志备顺序还原，时间点必须落在日志备份覆盖范围内。"),
"备份历史检查": ("backup-history",
"""SELECT TOP 20
       bs.database_name, bs.type, bs.backup_start_date, bs.backup_finish_date,
       bs.backup_size / 1024 / 1024 AS backup_size_mb,
       bmf.physical_device_name
FROM msdb.dbo.backupset AS bs
JOIN msdb.dbo.backupmediafamily AS bmf
  ON bs.media_set_id = bmf.media_set_id
ORDER BY bs.backup_finish_date DESC;""",
[], "type D=完整、I=差异、L=日志，恢复前先确认最近一次全备和日志备的时间。"),
"可用性组状态 / 同步延迟": ("ag-status-lag",
"""SELECT ar.replica_server_name, ars.role_desc,
       ars.availability_mode_desc, ars.synchronization_health_desc,
       ars.last_commit_time,
       DATEDIFF(SECOND, ars.last_commit_time, GETDATE()) AS lag_seconds
FROM sys.dm_hadr_availability_replica_states AS ars
JOIN sys.availability_replicas AS ar
  ON ars.replica_id = ar.replica_id
ORDER BY ars.role_desc;
SELECT TOP 20
       DB_NAME(database_id) AS db_name,
       log_send_queue_size, redo_queue_size, last_commit_time
FROM sys.dm_hadr_database_replica_states
ORDER BY log_send_queue_size DESC;""",
[], "同步延迟看 log_send_queue_size 和 redo_queue_size，健康状态看 synchronization_health_desc。"),
"故障转移演练清单": ("ag-failover",
"""-- 第 1 步：先查可用性组状态，确认目标副本已同步、健康
SELECT ar.replica_server_name, ars.role_desc, ars.synchronization_health_desc
FROM sys.dm_hadr_availability_replica_states AS ars
JOIN sys.availability_replicas AS ar
  ON ars.replica_id = ar.replica_id;
-- DANGER：只在演练窗口、确认业务可停写后执行，生产切换前先在测试环境演练
-- ALTER AVAILABILITY GROUP [<ag_name>] FAILOVER;""",
["ag_name"], "手动故障转移要求目标副本同步且健康，异步副本切换可能丢数据。"),
"登录名 / 用户 / 角色": ("logins-users-roles",
"""SELECT TOP 20 name, type_desc, is_disabled, create_date
FROM sys.server_principals
WHERE type IN ('S', 'U', 'G')
ORDER BY name;
SELECT TOP 20
       dp.name AS user_name, dp.type_desc,
       dr.name AS role_name
FROM sys.database_principals AS dp
LEFT JOIN sys.database_role_members AS drm
  ON drm.member_principal_id = dp.principal_id
LEFT JOIN sys.database_principals AS dr
  ON dr.principal_id = drm.role_principal_id
ORDER BY dp.name, dr.name;""",
[], "server_principals 是服务器登录名，database_principals 是库内用户，两者要分开查。"),
"审计（SQL Audit）": ("sql-audit",
"""SELECT name, is_state_enabled, type_desc, create_date
FROM sys.server_audits
ORDER BY name;
SELECT audit_id, name, status_desc, status_time
FROM sys.dm_server_audit_status;""",
[], "server_audits 看审计定义，dm_server_audit_status 看审计当前是否在运行。"),
}

def slugify(s):
    return s

def build(db_id, mapping):
    db = copy.deepcopy(DBS[db_id])
    # categories in order, subcategories in order; NN resets per subcategory
    for cat in db['categories']:
        for sub in cat['subcategories']:
            for idx, item in enumerate(sub['items'], start=1):
                slug, sql, params, notes = mapping[item['title']]
                item['sql'] = sql
                item['params'] = params
                item['notes'] = notes
                # write .sql file
                d = ROOT/'scripts'/('postgres' if db_id=='postgres' else 'sqlserver')/cat['name']
                d.mkdir(parents=True, exist_ok=True)
                fname = f"{idx:02d}-{slug}.sql"
                header = (f"-- {item['title']}\n-- 适用版本：{item['versions']}\n"
                          f"-- 风险：{item['risk']}\n-- 说明：{item['desc']}。{notes}\n"
                          f"-- 大类：{cat['name']} / 小类：{sub['name']}\n\n")
                (d/fname).write_text(header+sql.rstrip()+"\n", encoding='utf-8')
    out = ROOT/'data'/(f"toolbox-{'postgres' if db_id=='postgres' else 'sqlserver'}.json")
    out.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')
    n = sum(len(s['items']) for c in db['categories'] for s in c['subcategories'])
    print(db_id, n, out)
    return n

n1 = build('postgres', PG)
n2 = build('sqlserver', SS)
assert n1==26, n1
assert n2==20, n2
# verify mapping coverage: every title present
for db_id, m in [('postgres',PG),('sqlserver',SS)]:
    titles=[it['title'] for c in DBS[db_id]['categories'] for s in c['subcategories'] for it in s['items']]
    assert set(titles)==set(m.keys()), (db_id, set(titles)^set(m.keys()))
print("OK PG=26 SS=20")
