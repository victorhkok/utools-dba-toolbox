#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill Oracle 62 items: toolbox-oracle.json + scripts/oracle/<cat>/NN-slug.sql
Source of truth for title/versions/risk/desc: data/toolbox.json (Oracle part, unchanged).
"""
import json, pathlib, re
ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "data" / "toolbox.json"
OUT_JSON = ROOT / "data" / "toolbox-oracle.json"
SCRIPTS = ROOT / "scripts" / "oracle"

CAT_DIR = {
    "日常巡检": "日常巡检",
    "性能优化": "性能优化",
    "慢SQL": "慢SQL",
    "锁 / 会话 / 等待": "锁会话等待",
    "空间 / 存储": "空间存储",
    "备份恢复": "备份恢复",
    "高可用 / 容灾": "高可用容灾",
    "用户 / 权限 / 安全": "用户权限安全",
}

# title -> (slug, sql, params, notes)
E = {}
def add(title, slug, sql, params, notes):
    E[title] = {"slug": slug, "sql": sql.strip(), "params": params, "notes": notes}

add("实例状态 / 版本 / 启动时间", "instance-status",
"""SELECT i.instance_name,
       i.host_name,
       i.version,
       i.status,
       i.startup_time,
       d.name        AS db_name,
       d.open_mode,
       d.log_mode
FROM   v$instance i,
       v$database d;""",
[], "v$instance/v$database 均需 SYSDBA 或 SELECT_CATALOG_ROLE 权限；RAC 下每节点各查一次。")

add("监听与服务状态", "listener-status",
"""-- Shell / OS 命令（非 SQL，在数据库服务器上执行）：
-- lsnrctl status
-- srvctl status database -d <db_name>
-- srvctl status listener
-- crsctl check cluster -all        -- RAC 环境才有
-- 另查数据库内注册的服务：
SELECT name, network_name, failover_method
FROM   dba_services
ORDER  BY name;""",
["<db_name>"], "lsnrctl/srvctl 需在服务器 OS 执行，SQL*Plus 里跑不了；先确认 ORACLE_HOME/ORACLE_SID。")

add("数据库 / PDB 列表", "pdb-list",
"""SELECT name, cdb, open_mode, log_mode
FROM   v$database;

SELECT con_id, name, open_mode, restricted, total_size
FROM   v$pdbs
ORDER  BY con_id;""",
[], "仅 12c+ 有 v$pdbs / CDB 概念，11g 跑第二条会报 ORA-00942；先查 v$database.cdb 确认是否 CDB。")

add("无效对象清单", "invalid-objects",
"""SELECT owner, object_type, COUNT(*) AS cnt
FROM   dba_objects
WHERE  status = 'INVALID'
GROUP  BY owner, object_type
ORDER  BY cnt DESC;

-- 明细（前 50）：
SELECT *
FROM   (SELECT owner, object_name, object_type, status, last_ddl_time
        FROM   dba_objects
        WHERE  status = 'INVALID'
        ORDER  BY owner, object_type, object_name)
WHERE  ROWNUM <= 50;""",
[], "只列清单不自动编译；编译用 ALTER ... COMPILE，需先确认对象属主和依赖，生产慎做。")

add("定时任务 / 作业状态", "scheduler-jobs",
"""SELECT owner, job_name, job_type, state, enabled,
       last_start_date, next_run_date, failure_count
FROM   dba_scheduler_jobs
WHERE  owner NOT IN ('SYS', 'SYSTEM')
ORDER  BY owner, job_name;""",
[], "state=BROKEN/FAILURE 重点看；查单作业失败明细用 dba_scheduler_job_run_details。")

add("告警日志近24h错误", "alert-log-24h",
"""-- 1) 先查诊断目录（SQL）：
SELECT name, value
FROM   v$diag_info
WHERE  name IN ('Diag Trace', 'Diag Alert', 'Diag Incident');

-- 2) 再在服务器 OS 用 ADRCI（Shell）：
-- adrci exec="set homepath diag/rdbms/<db_name>/<sid>; show alert -term -tail 200"
-- 3) 常见错误直接 grep alert 日志：
-- grep -E "ORA-|TNS-" $ORACLE_BASE/diag/rdbms/<db_name>/<sid>/trace/alert_<sid>.log | tail -n 100""",
["<db_name>", "<sid>"], "ADRCI 的 homepath 按实际 diag 路径填；alert 日志不在数据库里，SQL 查不到内容，只能查路径。")

add("表空间使用率 Top", "tablespace-usage",
"""SELECT df.tablespace_name,
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
ORDER  BY pct_used DESC;""",
[], "使用率 >85% 预警，>95% 立即处理；临时表空间不在 dba_data_files 里，见“临时表空间使用”那条。")

add("归档日志生成量 / 切换频率", "archivelog-volume",
"""SELECT TRUNC(first_time) AS day,
       COUNT(*)             AS arch_count,
       ROUND(SUM(blocks * block_size) / 1024 / 1024, 2) AS mb_generated
FROM   v$archived_log
WHERE  first_time >= SYSDATE - 7
GROUP  BY TRUNC(first_time)
ORDER  BY day DESC;

-- 日志切换次数（近 7 天，按天）：
SELECT TRUNC(first_time) AS day, COUNT(*) AS switch_count
FROM   v$log_history
WHERE  first_time >= SYSDATE - 7
GROUP  BY TRUNC(first_time)
ORDER  BY day DESC;""",
[], "v$archived_log 只保留控制文件记录的归档，控制文件被覆盖后旧记录会丢；长期趋势以备份/监控为准。")

add("临时表空间使用", "temp-usage",
"""SELECT u.username,
       s.sid,
       s.serial#,
       u.tablespace,
       u.segtype,
       u.blocks,
       ROUND(u.blocks * 8192 / 1024 / 1024, 2) AS mb_used
FROM   v$tempseg_usage u
       JOIN v$session s ON u.session_addr = s.saddr
ORDER  BY u.blocks DESC;""",
[], "块大小按 8K 估算，不同库块大小用 SELECT value FROM v$parameter WHERE name='db_block_size' 核对；无行返回说明当前无人用临时段。")

add("UNDO 使用与保留", "undo-usage",
"""SELECT tablespace_name, retention
FROM   dba_tablespaces
WHERE  contents = 'UNDO';

SELECT TO_CHAR(begin_time, 'YYYY-MM-DD HH24:MI') AS begin_time,
       undoblks, txncount, maxquerylen, tuned_undoretention
FROM   v$undostat
WHERE  begin_time >= SYSDATE - 1
ORDER  BY begin_time DESC;""",
[], "tuned_undoretention 是自动调优后的建议保留秒数；ORA-01555 快照过旧先看 maxquerylen 和 UNDO 大小。")

add("生成 AWR 快照 / 报告", "awr-report",
"""-- 1) 查已有快照（近 1 天）：
SELECT snap_id, begin_interval_time, end_interval_time
FROM   dba_hist_snapshot
WHERE  begin_interval_time >= SYSDATE - 1
ORDER  BY snap_id DESC;

-- 2) 手动建一个快照（SQL*Plus / PL/SQL）：
-- EXEC DBMS_WORKLOAD_REPOSITORY.create_snapshot();

-- 3) 生成报告（SQL*Plus，在服务器上执行，选上面查到的起止 snap_id）：
-- @$ORACLE_HOME/rdbms/admin/awrrpt.sql
-- 按提示输入：html/text、起止 snap_id、报告文件名""",
["<snap_id_start>", "<snap_id_end>"], "AWR 需 Diagnostic Pack 授权，无授权不要用 dba_hist_*；create_snapshot 本身是写操作，虽列为只读条目，执行前确认授权。")

add("ASH Top 等待事件", "ash-top-events",
"""SELECT *
FROM   (SELECT event,
               wait_class,
               COUNT(*) AS samples,
               ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct
        FROM   v$active_session_history
        WHERE  sample_time >= SYSDATE - 1 / 24
          AND  event IS NOT NULL
        GROUP  BY event, wait_class
        ORDER  BY samples DESC)
WHERE  ROWNUM <= 20;""",
[], "v$active_session_history 是 1 秒采样，COUNT(*) 不是精确等待秒数，只能看占比；同样需 Diagnostic Pack 授权。")

add("DB Time / 负载画像", "db-time-profile",
"""SELECT stat_name,
       ROUND(value / 1000000, 2) AS seconds
FROM   v$sys_time_model
WHERE  stat_name IN ('DB time', 'DB CPU', 'background cpu time',
                     'sql execute elapsed time', 'parse time elapsed')
ORDER  BY value DESC;

-- 另查 AWR Load Profile 需 awrrpt.sql 报告里的 Load Profile 一节，本条只给 DB Time 总量。""",
[], "DB time 是所有前台会话 CPU+等待之和，可大于挂钟时间；DB time / 挂钟时间 ≈ 平均活跃会话数。")

add("SGA / PGA 使用与建议", "sga-pga-advice",
"""SELECT name, ROUND(value / 1024 / 1024, 2) AS mb
FROM   v$sga;

SELECT pga_target_for_estimate / 1024 / 1024 AS pga_target_mb,
       estd_pga_cache_hit_percentage,
       estd_overalloc_count
FROM   v$pga_target_advice
ORDER  BY pga_target_for_estimate;

SELECT name, value
FROM   v$pgastat
WHERE  name IN ('total PGA allocated', 'total PGA inuse', 'maximum PGA allocated');""",
[], "v$pga_target_advice 只在 PGA_AGGREGATE_TARGET 非 0 时有意义；SGA 改参数要重启或 ALTER SYSTEM，勿直接按建议值改生产。")

add("Buffer Cache 命中率", "buffer-cache-hit",
"""SELECT ROUND((1 - (SELECT value FROM v$sysstat WHERE name = 'physical reads')
                    / NULLIF((SELECT value FROM v$sysstat WHERE name = 'db block gets')
                             + (SELECT value FROM v$sysstat WHERE name = 'consistent gets'), 0)) * 100, 2) AS buffer_hit_pct
FROM   dual;

SELECT name, value
FROM   v$sysstat
WHERE  name IN ('db block gets', 'consistent gets', 'physical reads', 'physical reads cache')
ORDER  BY name;""",
[], "命中率是自启动累计值，重启后清零；单看命中率不够，全表扫描多的库命中率也可能虚高，要结合 Top SQL 看。")

add("Library Cache / 共享池", "library-cache",
"""SELECT namespace, gets, gethits,
       ROUND(gethits / NULLIF(gets, 0) * 100, 2) AS gethit_pct,
       pins, pinhits,
       ROUND(pinhits / NULLIF(pins, 0) * 100, 2) AS pinhit_pct,
       reloads, invalidations
FROM   v$librarycache
ORDER  BY namespace;""",
[], "reloads/invalidations 持续增长说明硬解析或对象频繁失效；先查共享池和绑定变量，不要直接调大 shared_pool。")

add("表 / 索引统计信息是否过期", "stale-stats",
"""SELECT *
FROM   (SELECT owner, table_name, num_rows, last_analyzed, stale_stats
        FROM   dba_tab_statistics
        WHERE  stale_stats = 'YES'
          AND  owner NOT IN ('SYS', 'SYSTEM', 'DBSNMP')
        ORDER  BY last_analyzed NULLS FIRST)
WHERE  ROWNUM <= 50;""",
[], "stale_stats='YES' 只表示 10% 行变化后未收集，不等于执行计划一定差；先看具体表的慢 SQL 再决定收集。")

add("收集统计信息（DBMS_STATS）", "gather-stats",
"""-- 先查（只读确认）：
SELECT owner, table_name, last_analyzed, stale_stats
FROM   dba_tab_statistics
WHERE  owner = '<schema>'
  AND  table_name = '<table_name>';

-- 再执行（谨慎：建议非高峰、测试库先跑）：
-- EXEC DBMS_STATS.gather_table_stats(ownname => '<schema>', tabname => '<table_name>', estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE, cascade => TRUE, degree => 4);
-- 整库模式：
-- EXEC DBMS_STATS.gather_schema_stats(ownname => '<schema>', estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE, cascade => TRUE, degree => 4);""",
["<schema>", "<table_name>"], "生产高峰不要全库收集；cascade=>TRUE 会连索引一起收集，degree 按 CPU 核数填，勿填过大。")

add("未使用索引清单", "unused-indexes",
"""SELECT index_name, table_name, monitoring, used,
       start_monitoring, end_monitoring
FROM   v$object_usage
WHERE  used = 'NO'
ORDER  BY table_name, index_name;

-- 开启监控（需先执行，跑一个业务周期后再查上条）：
-- ALTER INDEX <owner>.<index_name> MONITORING USAGE;""",
["<owner>", "<index_name>"], "v$object_usage 只有开过 MONITORING USAGE 的索引才有行；没监控过查不到不等于没用，勿直接删索引。")

add("缺失索引建议（SQL Tuning）", "missing-index-tuning",
"""-- 1) 建调优任务（需 Tuning Pack 授权）：
-- DECLARE l_task VARCHAR2(30);
-- BEGIN
--   l_task := DBMS_SQLTUNE.create_tuning_task(sql_id => '<sql_id>', scope => DBMS_SQLTUNE.scope_comprehensive, time_limit => 600);
--   DBMS_SQLTUNE.execute_tuning_task(task_name => l_task);
-- END;
-- /

-- 2) 查任务状态：
SELECT task_id, task_name, status, created
FROM   dba_advisor_tasks
WHERE  advisor_name = 'SQL Tuning Advisor'
ORDER  BY created DESC;

-- 3) 看报告（把 <task_name> 换成上条查到的）：
-- SELECT DBMS_SQLTUNE.report_tuning_task('<task_name>') FROM dual;""",
["<sql_id>", "<task_name>"], "把握一般：DBMS_SQLTUNE 需 Tuning Pack 授权，且 create_tuning_task 的返回值用法在不同版本有细节差异，生产先在测试库跑通再用。")

add("索引碎片 / 重建评估", "index-fragmentation",
"""SELECT *
FROM   (SELECT owner, index_name, table_name, blevel, leaf_blocks,
               distinct_keys, clustering_factor,
               ROUND(leaf_blocks * 8192 / 1024 / 1024, 2) AS leaf_mb
        FROM   dba_indexes
        WHERE  owner NOT IN ('SYS', 'SYSTEM')
        ORDER  BY leaf_blocks DESC)
WHERE  ROWNUM <= 20;

-- 重建模板（谨慎：先评估，勿直接执行）：
-- ALTER INDEX <owner>.<index_name> REBUILD ONLINE;""",
["<owner>", "<index_name>"], "blevel>4 或 leaf_blocks 明显偏大才考虑重建；ONLINE 重建仍需空间和锁评估，碎片不高时重建收益很小。")

add("Top SQL by Elapsed Time", "top-sql-elapsed",
"""SELECT *
FROM   (SELECT sql_id, executions,
               ROUND(elapsed_time / 1000000, 2) AS elapsed_sec,
               ROUND(elapsed_time / NULLIF(executions, 0) / 1000000, 2) AS avg_sec,
               buffer_gets, disk_reads,
               SUBSTR(sql_text, 1, 200) AS sql_text
        FROM   v$sql
        ORDER  BY elapsed_time DESC)
WHERE  ROWNUM <= 20;""",
[], "elapsed_time 单位是微秒；v$sql 是共享池累计值，实例重启后清零，长期 Top 以 AWR 为准。")

add("Top SQL by Buffer Gets", "top-sql-buffer-gets",
"""SELECT *
FROM   (SELECT sql_id, executions,
               buffer_gets,
               ROUND(buffer_gets / NULLIF(executions, 0), 0) AS gets_per_exec,
               ROUND(elapsed_time / 1000000, 2) AS elapsed_sec,
               SUBSTR(sql_text, 1, 200) AS sql_text
        FROM   v$sql
        ORDER  BY buffer_gets DESC)
WHERE  ROWNUM <= 20;""",
[], "逻辑读高不一定是慢 SQL，要结合 avg_sec 和执行次数看；先看 gets_per_exec 再决定是否优化。")

add("Top SQL by Executions", "top-sql-executions",
"""SELECT *
FROM   (SELECT sql_id, executions,
               ROUND(elapsed_time / NULLIF(executions, 0) / 1000000, 2) AS avg_sec,
               buffer_gets, disk_reads,
               SUBSTR(sql_text, 1, 200) AS sql_text
        FROM   v$sql
        ORDER  BY executions DESC)
WHERE  ROWNUM <= 20;""",
[], "执行次数多、单次不慢的 SQL 也值得优化，累计耗时可能最大；注意 v$sql_text 可能被截断。")

add("近1h 慢SQL（执行>5s）", "slow-sql-last-1h",
"""SELECT sql_id, executions,
       ROUND(elapsed_time / NULLIF(executions, 0) / 1000000, 2) AS avg_sec,
       ROUND(elapsed_time / 1000000, 2) AS total_sec,
       buffer_gets,
       SUBSTR(sql_text, 1, 200) AS sql_text
FROM   v$sql
WHERE  last_active_time >= SYSDATE - 1 / 24
  AND  executions > 0
  AND  elapsed_time / executions > 5000000
ORDER  BY avg_sec DESC;""",
[], "5 秒阈值是 elapsed_time/executions > 5,000,000 微秒；last_active_time 是最后活跃时间，不是首次执行时间。")

add("查看执行计划（EXPLAIN PLAN）", "explain-plan",
"""-- 模板：把 <你的SQL> 换成要分析的语句（不带分号结尾的分号外写法见下）
EXPLAIN PLAN FOR
SELECT * FROM <schema>.<table_name> WHERE <condition>;

SELECT * FROM TABLE(DBMS_XPLAN.display);""",
["<schema>", "<table_name>", "<condition>"], "EXPLAIN PLAN 是预估计划，不代表真实执行；要真实行数用 DISPLAY_CURSOR 或加 GATHER_PLAN_STATISTICS Hint。")

add("真实执行计划（DBMS_XPLAN.DISPLAY_CURSOR）", "display-cursor",
"""SELECT * FROM TABLE(DBMS_XPLAN.display_cursor('<sql_id>', <child_number>, 'ALLSTATS LAST'));

-- 查该 SQL 的 child_number：
SELECT sql_id, child_number, executions, plan_hash_value
FROM   v$sql
WHERE  sql_id = '<sql_id>'
ORDER  BY child_number;""",
["<sql_id>", "<child_number>"], "'ALLSTATS LAST' 只有 SQL 带 /*+ GATHER_PLAN_STATISTICS */ 或 statistics_level=ALL 时才有 A-Rows/Buffers，否则只显示预估。")

add("全表扫描 SQL 清单", "full-table-scan-sql",
"""SELECT p.sql_id,
       COUNT(*) AS full_scan_ops,
       MAX(s.executions) AS executions,
       SUBSTR(MAX(s.sql_text), 1, 200) AS sql_text
FROM   v$sql_plan p
       JOIN v$sql s ON p.sql_id = s.sql_id AND p.child_number = s.child_number
WHERE  p.operation = 'TABLE ACCESS'
  AND  p.options = 'FULL'
GROUP  BY p.sql_id
ORDER  BY full_scan_ops DESC;""",
[], "v$sql_plan 只保留共享池里的计划，重启后丢失；小表全表扫描是正常的，先看表大小和执行次数再优化。")

add("绑定变量窥探 / 直方图检查", "bind-capture-histogram",
"""SELECT sql_id, name, position, datatype_string, value_string, last_captured
FROM   v$sql_bind_capture
WHERE  sql_id = '<sql_id>'
ORDER  BY position;

-- 直方图（只列有直方图的列）：
SELECT owner, table_name, column_name, histogram, num_distinct
FROM   dba_tab_col_statistics
WHERE  histogram <> 'NONE'
  AND  owner = '<schema>'
ORDER  BY table_name, column_name;""",
["<sql_id>", "<schema>"], "v$sql_bind_capture 只保留最近一次捕获的绑定值，不代表每次执行的值；直方图过期会导致绑定窥探失真。")

add("SQL Profile / Baseline 建议", "sql-profile-baseline",
"""-- 1) 先跑调优任务并看报告（见“缺失索引建议”那条，任务名换成实际值）：
-- SELECT DBMS_SQLTUNE.report_tuning_task('<task_name>') FROM dual;

-- 2) 查已有 Profile / Baseline：
SELECT name, type, status, created
FROM   dba_sql_profiles
ORDER  BY created DESC;

SELECT sql_handle, plan_name, enabled, accepted, origin
FROM   dba_sql_plan_baselines
ORDER  BY created DESC;

-- 3) 接受 Profile 模板（谨慎：先在测试库验证）：
-- EXEC DBMS_SQLTUNE.accept_sql_profile(task_name => '<task_name>', name => '<profile_name>');""",
["<task_name>", "<profile_name>"], "接受 Profile 会改变执行计划，生产先在测试库验证；Baseline 需先用 DBMS_SPM.load_plans_from_cursor_cache 加载。")

add("自动索引建议（19c+）", "auto-index-19c",
"""-- 查自动索引配置：
SELECT parameter_name, parameter_value
FROM   dba_auto_index_config
ORDER  BY parameter_name;

-- 查已自动创建的索引：
SELECT index_name, table_owner, table_name, auto
FROM   dba_indexes
WHERE  auto = 'YES'
ORDER  BY table_name;

-- 查最近自动索引活动报告：
-- SELECT DBMS_AUTO_INDEX.report_last_activity() FROM dual;""",
[], "把握一般：DBA_AUTO_INDEX_CONFIG 的列名/参数名在 19c 各补丁间有细节差异，且自动索引默认不开启；本条先以查询为准，开启前务必在测试库核对视图定义。")

add("Hint 改写模板", "hint-template",
"""-- 模板（谨慎：Hint 只在确认执行计划走偏时用，先在测试库对比前后计划）：
-- SELECT /*+ INDEX(t <index_name>) */ * FROM <schema>.<table_name> t WHERE <condition>;
-- SELECT /*+ PARALLEL(t, 4) */ * FROM <schema>.<table_name> t WHERE <condition>;
-- SELECT /*+ LEADING(a b) USE_HASH(b) */ * FROM <schema>.<table_a> a, <schema>.<table_b> b WHERE a.id = b.id;

-- 查当前带 Hint 的 SQL（前 20）：
SELECT sql_id, SUBSTR(sql_text, 1, 200) AS sql_text
FROM   v$sql
WHERE  sql_text LIKE '%/*+%'
  AND  ROWNUM <= 20;""",
["<schema>", "<table_name>", "<index_name>", "<condition>"], "Hint 写错表别名/索引名会被优化器静默忽略；改完务必用 DISPLAY_CURSOR 确认计划真的变了。")

add("当前阻塞锁链", "blocking-chain",
"""SELECT sid, serial#, username, machine, program, status,
       blocking_session, blocking_session_serial#,
       event, sql_id,
       ROUND((SYSDATE - logon_time) * 24 * 60, 1) AS mins_since_logon
FROM   v$session
WHERE  blocking_session IS NOT NULL
   OR  sid IN (SELECT blocking_session FROM v$session WHERE blocking_session IS NOT NULL)
ORDER  BY blocking_session NULLS FIRST, sid;

-- 锁详情（v$lock）：
SELECT l.sid, l.type, l.lmode, l.request, l.block, s.username
FROM   v$lock l
       JOIN v$session s ON l.sid = s.sid
WHERE  l.block = 1 OR l.request > 0
ORDER  BY l.sid;""",
[], "blocking_session 为空不代表没锁，可能是行锁在等 TX；先找根阻塞者（blocking_session 为空的那行），不要先杀等待者。")

add("死锁历史（ORA-00060）", "deadlock-history",
"""-- 1) 查诊断目录（SQL）：
SELECT name, value
FROM   v$diag_info
WHERE  name IN ('Diag Trace', 'Diag Alert');

-- 2) 在服务器 OS 上 grep alert 日志（Shell）：
-- grep -i "ORA-00060" $ORACLE_BASE/diag/rdbms/<db_name>/<sid>/trace/alert_<sid>.log | tail -n 20
-- 3) 找到死锁 trace 文件名（alert 日志里 Deadlock graph 一节会给 trace 文件路径，再用 vi / less 打开看）""",
["<db_name>", "<sid>"], "死锁信息不在 v$ 视图里，只能看 alert 日志和 trace 文件；本条 SQL 只能定位日志路径，不能直接查出死锁 SQL。")

add("行锁等待详情", "row-lock-wait",
"""SELECT s.sid, s.serial#, s.username, s.event, s.seconds_in_wait,
       s.row_wait_obj#, s.row_wait_file#, s.row_wait_block#, s.row_wait_row#,
       o.object_name, o.object_type
FROM   v$session s
       LEFT JOIN dba_objects o ON o.object_id = s.row_wait_obj#
WHERE  s.event LIKE 'enq: TX%'
   OR  s.wait_class = 'Application'
ORDER  BY s.seconds_in_wait DESC;""",
[], "row_wait_* 只在会话正在等行锁时有值，锁释放后就没了；要定位行内容需按 file#/block#/row# 再查表，生产慎做。")

add("杀会话（ALTER SYSTEM KILL）", "kill-session",
"""-- 第 1 步：先确认要杀的会话（只读）：
SELECT sid, serial#, username, machine, program, status, sql_id, event
FROM   v$session
WHERE  sid = <sid>
  AND  serial# = <serial#>;

-- 第 2 步：确认无误后再执行（DANGER：会中断业务会话，RAC 需加 @inst_id）：
-- ALTER SYSTEM KILL SESSION '<sid>,<serial#>' IMMEDIATE;
-- RAC 写法：
-- ALTER SYSTEM KILL SESSION '<sid>,<serial#>,@<inst_id>' IMMEDIATE;""",
["<sid>", "<serial#>", "<inst_id>"], "DANGER：先确认 sid+serial# 对应的是目标会话而非后台进程；KILL 后会话可能要等 PMON 清理回滚，勿重复 KILL。")

add("活跃会话 Top", "active-sessions",
"""SELECT *
FROM   (SELECT sid, serial#, username, machine, program, status,
               event, sql_id,
               ROUND((SYSDATE - logon_time) * 24 * 60, 1) AS mins_since_logon
        FROM   v$session
        WHERE  status = 'ACTIVE'
          AND  type = 'USER'
        ORDER  BY logon_time)
WHERE  ROWNUM <= 20;""",
[], "ACTIVE 只表示此刻在跑 SQL，不等于长耗时；结合 sql_id 和 event 看，不要只按 logon_time 排序就杀。")

add("等待事件 Top 10", "wait-events-top10",
"""SELECT *
FROM   (SELECT event, total_waits,
               ROUND(time_waited / 100, 2) AS waited_sec,
               ROUND(time_waited_micro / 1000000, 2) AS waited_sec_micro,
               total_timeouts
        FROM   v$system_event
        WHERE  event NOT LIKE 'SQL*Net%'
          AND  event NOT LIKE 'rdbms ipc%'
        ORDER  BY time_waited DESC)
WHERE  ROWNUM <= 10;""",
[], "time_waited 单位是百分之一秒，time_waited_micro 是微秒，两者不要混用；idle 类事件已过滤，仍需结合 ASH 看。")

add("长运行会话（>30min）", "long-running-sessions",
"""SELECT sid, serial#, username, sql_id, event,
       last_call_et,
       ROUND(last_call_et / 60, 1) AS mins_running,
       ROUND((SYSDATE - logon_time) * 24 * 60, 1) AS mins_since_logon
FROM   v$session
WHERE  status = 'ACTIVE'
  AND  type = 'USER'
  AND  last_call_et > 1800
ORDER  BY last_call_et DESC;""",
[], "last_call_et 是当前调用已持续秒数，不是整个会话时长；>1800 秒即 30 分钟，勿把空闲会话（last_call_et 大但 status=INACTIVE）算进来。")

add("表空间扩容（ADD DATAFILE）", "add-datafile",
"""-- 第 1 步：先查表空间和磁盘（只读）：
SELECT tablespace_name, file_name,
       ROUND(bytes / 1024 / 1024, 2) AS mb,
       autoextensible,
       ROUND(maxbytes / 1024 / 1024, 2) AS max_mb
FROM   dba_data_files
WHERE  tablespace_name = '<tablespace_name>'
ORDER  BY file_id;

-- 第 2 步：确认磁盘余量（Shell：df -h <datafile_dir>），确认后再执行（DANGER）：
-- ALTER TABLESPACE <tablespace_name> ADD DATAFILE '<datafile_path>' SIZE 1G AUTOEXTEND ON NEXT 100M MAXSIZE UNLIMITED;""",
["<tablespace_name>", "<datafile_path>", "<datafile_dir>"], "DANGER：先确认磁盘余量和文件路径权限；SIZE/MAXSIZE 按实际剩余空间填，不要照抄 1G/UNLIMITED。")

add("数据文件 / 自动扩展状态", "datafiles-autoextend",
"""SELECT tablespace_name, file_name,
       ROUND(bytes / 1024 / 1024, 2) AS mb,
       ROUND(maxbytes / 1024 / 1024, 2) AS max_mb,
       autoextensible, increment_by
FROM   dba_data_files
ORDER  BY tablespace_name, file_id;""",
[], "maxbytes=0 表示未设上限或不可扩展，要结合 autoextensible 看；increment_by 单位是块，不是 MB。")

add("段增长 Top 20", "segment-growth-top20",
"""SELECT *
FROM   (SELECT owner, segment_name, segment_type, tablespace_name,
               ROUND(bytes / 1024 / 1024, 2) AS mb
        FROM   dba_segments
        ORDER  BY bytes DESC)
WHERE  ROWNUM <= 20;""",
[], "dba_segments 是当前大小，不是增长量；要增长趋势需定期快照对比，或查 dba_hist_seg_stat（需 Diagnostic Pack）。")

add("大表 / 大索引清单", "large-tables-indexes",
"""SELECT *
FROM   (SELECT owner, segment_name, segment_type, tablespace_name,
               ROUND(bytes / 1024 / 1024, 2) AS mb
        FROM   dba_segments
        WHERE  segment_type IN ('TABLE', 'INDEX')
        ORDER  BY bytes DESC)
WHERE  ROWNUM <= 20;""",
[], "只按段大小排，分区表会拆成多个段；要整表大小需按 segment_name 去掉分区后缀汇总。")

add("回收站清理（PURGE）", "purge-recyclebin",
"""SELECT owner, object_name, original_name, type, ts_name, droptime,
       ROUND(space * 8192 / 1024 / 1024, 2) AS mb
FROM   dba_recyclebin
ORDER  BY droptime DESC;

-- 清理模板（谨慎：PURGE 后无法 FLASHBACK 恢复）：
-- PURGE TABLE <owner>.<object_name>;
-- PURGE RECYCLEBIN;""",
["<owner>", "<object_name>"], "PURGE 后 DROP 的表无法再闪回恢复；先确认 droptime 和 original_name 是要删的表，再执行。")

add("RMAN 全量备份命令", "rman-full-backup",
"""-- RMAN 命令（在 RMAN 提示符或 rman target / @脚本 里执行）：
RUN {
  ALLOCATE CHANNEL c1 DEVICE TYPE DISK FORMAT '<backup_dir>/%d_%T_%U.bak';
  BACKUP DATABASE PLUS ARCHIVELOG;
  DELETE NOPROMPT OBSOLETE;
  RELEASE CHANNEL c1;
}""",
["<backup_dir>"], "PLUS ARCHIVELOG 会先切归档再备份；DELETE OBSOLETE 按保留策略删旧备份，执行前先 SHOW RETENTION POLICY 确认。")

add("RMAN 增量 0/1 级备份", "rman-incremental-backup",
"""-- 0 级（全量基准，含归档）：
RUN {
  ALLOCATE CHANNEL c1 DEVICE TYPE DISK FORMAT '<backup_dir>/%d_%T_L0_%U.bak';
  BACKUP INCREMENTAL LEVEL 0 DATABASE PLUS ARCHIVELOG;
  RELEASE CHANNEL c1;
}

-- 1 级（差异增量，日常跑）：
-- RUN {
--   ALLOCATE CHANNEL c1 DEVICE TYPE DISK FORMAT '<backup_dir>/%d_%T_L1_%U.bak';
--   BACKUP INCREMENTAL LEVEL 1 DATABASE PLUS ARCHIVELOG;
--   RELEASE CHANNEL c1;
-- }""",
["<backup_dir>"], "0 级是 1 级的基准，1 级恢复要依赖最近的 0 级；先做 0 级再做 1 级，不要只跑 1 级。")

add("RMAN 备份集 / 保留策略检查", "rman-backup-check",
"""-- RMAN 命令（只读检查）：
-- LIST BACKUP SUMMARY;
-- LIST BACKUP OF DATABASE SUMMARY;
-- SHOW RETENTION POLICY;
-- SHOW ALL;
-- REPORT OBSOLETE;
-- REPORT NEED BACKUP;""",
[], "LIST/REPORT 是 RMAN 命令不是 SQL，在 SQL*Plus 里跑不了；REPORT OBSOLETE 只报告不删除，删除用 DELETE OBSOLETE。")

add("RMAN 恢复演练清单", "rman-restore-rehearsal",
"""-- 演练清单（只在测试库/演练环境执行，勿在生产直接跑）：
-- 1. LIST BACKUP SUMMARY;              -- 确认最近一次全备+归档都在
-- 2. SHOW RETENTION POLICY;            -- 确认保留策略
-- 3. RESTORE DATABASE PREVIEW;         -- 预演恢复，不真正写文件
-- 4. VALIDATE DATABASE;                -- 校验备份可读
-- 5. RESTORE DATABASE; RECOVER DATABASE; ALTER DATABASE OPEN RESETLOGS;
--    -- 第 5 步只在演练库执行，生产恢复按实际故障场景走，勿照抄 RESETLOGS""",
[], "把握一般：本条是演练清单不是单条可执行 SQL，RESTORE/RECOVER 的具体语法随场景（全库/表空间/时间点）而变，演练前先做全备。")

add("闪回查询（AS OF TIMESTAMP）", "flashback-query",
"""-- 查 1 小时前的数据（模板）：
SELECT * FROM <schema>.<table_name> AS OF TIMESTAMP (SYSDATE - 1 / 24) WHERE ROWNUM <= 20;

-- 先确认 UNDO 能保留多久（只读）：
SELECT TO_CHAR(begin_time, 'YYYY-MM-DD HH24:MI') AS begin_time,
       tuned_undoretention, maxquerylen
FROM   v$undostat
WHERE  begin_time >= SYSDATE - 1
ORDER  BY begin_time DESC;""",
["<schema>", "<table_name>"], "超过 UNDO 保留期会报 ORA-01555；闪回查询只能读，不能直接 UPDATE 回去，要恢复需 INSERT SELECT。")

add("闪回表（FLASHBACK TABLE）", "flashback-table",
"""-- 第 1 步：先确认行移动是否开启（只读）：
SELECT owner, table_name, row_movement
FROM   dba_tables
WHERE  owner = '<schema>'
  AND  table_name = '<table_name>';

-- 第 2 步：确认后再执行（DANGER：会回退整表到指定时间点）：
-- ALTER TABLE <schema>.<table_name> ENABLE ROW MOVEMENT;
-- FLASHBACK TABLE <schema>.<table_name> TO TIMESTAMP TO_TIMESTAMP('<yyyy-mm-dd hh24:mi:ss>', 'YYYY-MM-DD HH24:MI:SS');""",
["<schema>", "<table_name>", "<yyyy-mm-dd hh24:mi:ss>"], "DANGER：需先 ENABLE ROW MOVEMENT；闪回表会回退该时间点之后的所有 DML，执行前先闪回查询确认数据。")

add("RMAN 表级 PITR", "rman-table-pitr",
"""-- 12c+ 才支持 RECOVER TABLE，先确认版本和备份（只读）：
-- SELECT * FROM v$version;
-- LIST BACKUP OF TABLE <schema>.<table_name>;

-- 恢复模板（DANGER：只在演练/恢复场景执行，12c+）：
-- RECOVER TABLE <schema>.<table_name>
--   UNTIL TIME "TO_DATE('<yyyy-mm-dd hh24:mi:ss>', 'YYYY-MM-DD HH24:MI:SS')"
--   AUXILIARY DESTINATION '<aux_dir>';""",
["<schema>", "<table_name>", "<yyyy-mm-dd hh24:mi:ss>", "<aux_dir>"], "仅 12c+ 支持，11g 跑会报错；AUXILIARY DESTINATION 需有足够空间放辅助实例，恢复耗时按表大小估算。")

add("块损坏 BMR 恢复", "block-media-recovery",
"""-- 第 1 步：先查坏块（只读）：
SELECT file#, block#, blocks, corruption_type
FROM   v$database_block_corruption
ORDER  BY file#, block#;

-- 第 2 步：校验备份（RMAN）：
-- VALIDATE DATABASE;

-- 第 3 步：块恢复模板（DANGER：需有备份，确认 file#/block# 后再执行）：
-- BLOCKRECOVER DATAFILE <file#> BLOCK <block#>;""",
["<file#>", "<block#>"], "DANGER：v$database_block_corruption 为空不代表没坏块，要 VALIDATE 才准；BLOCKRECOVER 需 RMAN 备份，没有备份无法恢复。")

add("RAC 节点 / 实例状态", "rac-status",
"""-- SQL（gv$instance，各节点一行）：
SELECT inst_id, instance_name, host_name, version, status, startup_time
FROM   gv$instance
ORDER  BY inst_id;

-- Shell（服务器上执行）：
-- crsctl check cluster -all
-- srvctl status database -d <db_name>
-- srvctl status instance -d <db_name> -i <inst_name>""",
["<db_name>", "<inst_name>"], "gv$instance 需 RAC 环境，单机跑只有一行；crsctl/srvctl 需 grid 用户权限。")

add("RAC 互联 / 心跳检查", "rac-interconnect",
"""SELECT inst_id, name, ip_address, is_public, source
FROM   gv$cluster_interconnects
ORDER  BY inst_id;

-- Shell（服务器上执行）：
-- oifcfg getif
-- crsctl check cssd
-- crsctl stat res -t""",
[], "互联（private）丢包会触发节点驱逐；is_public='NO' 的才是互联，勿把公网 IP 当互联。")

add("服务切换 / 负载均衡检查", "rac-service",
"""SELECT name, network_name, failover_method, failover_type, failover_retries
FROM   dba_services
ORDER  BY name;

-- Shell（服务器上执行）：
-- srvctl config service -d <db_name>
-- srvctl status service -d <db_name>""",
["<db_name>"], "dba_services 看的是数据库内服务定义，实际运行状态以 srvctl status 为准；改服务要 srvctl modify，不要直接改表。")

add("DG 备库延迟（Apply Lag）", "dg-lag",
"""SELECT name, value, time_computed, datum_time
FROM   v$dataguard_stats;

SELECT database_role, protection_mode, switchover_status, open_mode
FROM   v$database;""",
[], "apply lag 和 transport lag 是两个值，v$dataguard_stats 里分开列；备库查要在备库上执行，主库查不到备库延迟。")

add("DG 切换演练（Switchover）", "dg-switchover",
"""-- 第 1 步：先确认可切换（只读，主备都查）：
SELECT database_role, switchover_status, open_mode
FROM   v$database;

-- 第 2 步：确认 switchover_status=TO STANDBY / TO PRIMARY 后再执行（DANGER：会切主备角色）：
-- 主库执行：ALTER DATABASE COMMIT TO SWITCHOVER TO PHYSICAL STANDBY;
-- 备库执行：ALTER DATABASE COMMIT TO SWITCHOVER TO PRIMARY;
-- 然后两边分别 SHUTDOWN / STARTUP，按实际演练手册走""",
[], "DANGER：演练前必须停写确认，switchover_status 不是 TO STANDBY/TO PRIMARY 时不要强行切；RAC 切换步骤与单机不同。")

add("OGG 抽取 / 投递延迟", "ogg-lag",
"""-- GGSCI 命令（在 OGG 安装目录执行 ./ggsci，非 SQL）：
-- INFO ALL
-- INFO EXTRACT <extract_name>
-- INFO REPLICAT <replicat_name>
-- LAG EXTRACT <extract_name>
-- LAG REPLICAT <replicat_name>
-- INFO EXTRACT <extract_name>, DETAIL""",
["<extract_name>", "<replicat_name>"], "把握一般：OGG 不是数据库内置功能，命令在 GGSCI 里执行，LAG 数值单位和版本有关；先确认 OGG 版本和进程名再查。")

add("容灾 RPO=0 演练清单", "rpo0-rehearsal",
"""-- 演练前只读检查：
SELECT database_role, protection_mode, switchover_status FROM v$database;
SELECT name, value FROM v$dataguard_stats;
-- LIST BACKUP SUMMARY;  -- RMAN，确认最近全备
-- 演练清单（只在演练环境执行）：
-- 1. 确认 DG apply lag = 0、归档无缺口（v$archived_log gap 检查）
-- 2. 确认 RMAN 最近全备+归档可恢复（VALIDATE DATABASE）
-- 3. 按演练手册做 Switchover / Failover，记录切换耗时
-- 4. 切回后确认主备角色、应用连接、数据一致性抽查""",
[], "把握一般：本条是演练清单，RPO=0 依赖同步模式（MAXIMUM PROTECTION/AVAILABILITY）+网络，清单本身不保证 RPO=0，演练前先核对保护模式。")

add("用户 / 角色 / 权限清单", "user-privileges",
"""SELECT username, account_status, default_tablespace, temporary_tablespace, profile, created
FROM   dba_users
ORDER  BY username;

SELECT grantee, granted_role, admin_option
FROM   dba_role_privs
WHERE  grantee = '<username>'
ORDER  BY granted_role;

SELECT grantee, privilege, admin_option
FROM   dba_sys_privs
WHERE  grantee = '<username>'
ORDER  BY privilege;""",
["<username>"], "dba_users/dba_role_privs/dba_sys_privs 均需 DBA 权限；查单个用户时把 <username> 换成大写用户名。")

add("密码过期 / 锁定账号", "locked-expired-users",
"""SELECT username, account_status, lock_date, expiry_date, profile
FROM   dba_users
WHERE  account_status <> 'OPEN'
ORDER  BY username;

-- 即将过期（30 天内）：
SELECT username, account_status, expiry_date
FROM   dba_users
WHERE  expiry_date IS NOT NULL
  AND  expiry_date < SYSDATE + 30
ORDER  BY expiry_date;""",
[], "account_status 含 EXPIRED(GRACE) 等多种状态，不等于锁定；解锁用 ALTER USER ... ACCOUNT UNLOCK，属谨慎操作勿批量执行。")

add("审计开启与审计日志", "audit-log",
"""-- 1) 查审计开关（SQL*Plus）：
-- SHOW PARAMETER audit_trail;

-- 2) 11g 传统审计日志（近 1 天，前 50）：
SELECT username, action_name, timestamp, obj_name, returncode
FROM   dba_audit_trail
WHERE  timestamp >= SYSDATE - 1
  AND  ROWNUM <= 50
ORDER  BY timestamp DESC;

-- 3) 12c+ 统一审计（仅 12c+，11g 跑会报 ORA-00942）：
-- SELECT dbusername, action_name, event_timestamp, object_name, return_code
-- FROM   unified_audit_trail
-- WHERE  event_timestamp >= SYSDATE - 1
--   AND  ROWNUM <= 50
-- ORDER  BY event_timestamp DESC;""",
[], "11g 用 dba_audit_trail，12c+ 推荐 unified_audit_trail；SHOW PARAMETER 是 SQL*Plus 命令，在 JDBC 里跑不了。")

# ---------- build ----------
data = json.loads(SRC.read_text(encoding="utf-8"))
oracle = next(d for d in data["databases"] if d["id"] == "oracle")
count = 0
missing = []
for cat in oracle["categories"]:
    cat_dir = CAT_DIR[cat["name"]]
    for sub in cat["subcategories"]:
        for idx, item in enumerate(sub["items"], start=1):
            title = item["title"]
            if title not in E:
                missing.append(title); continue
            e = E[title]
            item["sql"] = e["sql"]
            item["params"] = e["params"]
            item["notes"] = e["notes"]
            count += 1
            # write .sql file
            d = SCRIPTS / cat_dir
            d.mkdir(parents=True, exist_ok=True)
            fname = f"{idx:02d}-{e['slug']}.sql"
            header = (f"-- {title}\n-- 适用版本：{item['versions']}\n-- 风险：{item['risk']}\n"
                      f"-- 说明：{item['desc']}\n-- 提醒：{e['notes']}\n")
            (d / fname).write_text(header + "\n" + e["sql"] + "\n", encoding="utf-8")
assert not missing, f"missing: {missing}"
assert count == 62, f"count={count}"
# output: Oracle object only, same structure as toolbox.json Oracle part
out = {"id": oracle["id"], "name": oracle["name"], "versions": oracle["versions"],
       "note": oracle["note"], "categories": oracle["categories"]}
OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"ok count={count} json={OUT_JSON}")
for cat in oracle["categories"]:
    print(cat["name"], sum(len(s["items"]) for s in cat["subcategories"]))
