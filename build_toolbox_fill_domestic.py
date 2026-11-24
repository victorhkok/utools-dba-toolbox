#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill DM/OB/GBase/TiDB/Common (62 items) with real SQL/commands.
Source of truth: data/toolbox.json - titles/versions/risk/desc are copied verbatim,
only sql/params/notes are added. No items added/removed.
"""
import json, pathlib, re
ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "data" / "toolbox.json"
DATA = json.loads(SRC.read_text(encoding="utf-8"))
DBS = {b["id"]: b for b in DATA["databases"]}

# FILL[(db_id, title)] = dict(sql=..., params=[...], notes="...", slug="...")
F = {}
def add(db, title, slug, sql, params=None, notes=""):
    F[(db, title)] = {"slug": slug, "sql": sql.strip(), "params": params or [], "notes": notes}

# ================= 达梦 DM8 (16) =================
add("dameng","实例状态 / 版本","instance-status",
"""SELECT NAME, INSTANCE_NAME, VERSION, STATUS, STARTUP_TIME, MODE$ AS MODE FROM V$INSTANCE;""",
[],"DM8 视图 V$INSTANCE，需 DBA 或相应查询权限。")
add("dameng","表空间 / 数据文件","tablespace-datafiles",
"""SELECT T.TABLESPACE_NAME, T.STATUS, T.CONTENTS, F.FILE_NAME, F.BYTES/1024/1024 AS SIZE_MB, F.AUTOEXTENSIBLE
FROM DBA_TABLESPACES T LEFT JOIN DBA_DATA_FILES F ON T.TABLESPACE_NAME = F.TABLESPACE_NAME
ORDER BY T.TABLESPACE_NAME, F.FILE_NAME;""",
[],"DBA_TABLESPACES / DBA_DATA_FILES 为 DM8 兼容 Oracle 的数据字典视图。")
add("dameng","缓存命中率 / 内存","bufferpool-hit-ratio",
"""SELECT TOP 20 NAME, (1 - PHYSICAL_READS / NULLIF(GETS, 0)) * 100 AS HIT_RATIO_PCT, GETS, PHYSICAL_READS
FROM V$BUFFERPOOL
ORDER BY NAME;""",
[],"V$BUFFERPOOL 列名需在 DM8 实测核对，GETS/PHYSICAL_READS 为 0 时结果为 NULL。")
add("dameng","统计信息收集","gather-table-stats",
"""-- 先确认表名与 schema，再执行（建议非高峰）：
-- DANGER: DBMS_STATS.GATHER_TABLE_STATS('<SCHEMA>', '<TABLE>');
SELECT TABLE_NAME, LAST_ANALYZED, NUM_ROWS FROM DBA_TABLES WHERE OWNER = '<SCHEMA>' AND TABLE_NAME = '<TABLE>';""",
[{"name":"SCHEMA","desc":"模式名"},{"name":"TABLE","desc":"表名"}],
"DM8 的 DBMS_STATS 与 Oracle 兼容，但参数细节需在 DM8 实测核对。")
add("dameng","慢SQL Top（V$SQL）","slow-sql-top",
"""SELECT TOP 20 SQL_TEXT, ELAPSED_TIME, EXECUTIONS, ROWS_PROCESSED
FROM V$SQL
WHERE ELAPSED_TIME > 0
ORDER BY ELAPSED_TIME DESC;""",
[],"V$SQL 在 DM8 中的列名（ELAPSED_TIME/ROWS_PROCESSED）需在 DM8 实测核对。")
add("dameng","执行计划（EXPLAIN）","explain-plan",
"""EXPLAIN SELECT * FROM <SCHEMA>.<TABLE> WHERE <CONDITION>;""",
[{"name":"SCHEMA.TABLE","desc":"表名"},{"name":"CONDITION","desc":"WHERE 条件"}],
"DM8 支持 EXPLAIN，输出格式与 Oracle 的 DBMS_XPLAN 不同，需在 DM8 实测核对。")
add("dameng","阻塞锁 / 会话","blocking-locks",
"""SELECT TOP 20 L.SESS_ID AS BLOCKED_SESS, L.TRX_ID, S.USERNAME, S.CLIENT_IP, S.SQL_TEXT
FROM V$LOCK L JOIN V$SESSIONS S ON L.SESS_ID = S.SESS_ID
WHERE L.BLOCKED = 1
ORDER BY L.SESS_ID;""",
[],"V$LOCK/V$SESSIONS 的阻塞标志列名需在 DM8 实测核对，如无 BLOCKED 列请改查 V$LOCK 全量。")
add("dameng","杀会话","kill-session",
"""-- 1. 先确认（只读查询）：
SELECT SESS_ID, USERNAME, CLIENT_IP, SQL_TEXT FROM V$SESSIONS WHERE SESS_ID = <SESS_ID>;
-- 2. 确认无误后再执行（危险）：
-- DANGER: SP_CLOSE_SESSION(<SESS_ID>);""",
[{"name":"SESS_ID","desc":"会话 ID"}],
"SP_CLOSE_SESSION 需 DBA 权限，杀会话前务必确认业务影响。")
add("dameng","表空间使用率","tablespace-usage",
"""SELECT TOP 20 T.TABLESPACE_NAME, ROUND(SUM(F.BYTES)/1024/1024, 2) AS TOTAL_MB,
  ROUND((SUM(F.BYTES) - MAX(NVL(FREE.BYTES, 0)))/1024/1024, 2) AS USED_MB,
  ROUND((1 - MAX(NVL(FREE.BYTES, 0))/SUM(F.BYTES)) * 100, 2) AS USED_PCT
FROM DBA_DATA_FILES F
JOIN DBA_TABLESPACES T ON F.TABLESPACE_NAME = T.TABLESPACE_NAME
LEFT JOIN (SELECT TABLESPACE_NAME, SUM(BYTES) BYTES FROM DBA_FREE_SPACE GROUP BY TABLESPACE_NAME) FREE
  ON FREE.TABLESPACE_NAME = T.TABLESPACE_NAME
GROUP BY T.TABLESPACE_NAME
ORDER BY USED_PCT DESC;""",
[],"DBA_FREE_SPACE 在 DM8 中的列名需在 DM8 实测核对，>85% 预警。")
add("dameng","大表 Top","large-tables-top",
"""SELECT TOP 20 OWNER, SEGMENT_NAME, SEGMENT_TYPE, ROUND(BYTES/1024/1024, 2) AS SIZE_MB
FROM DBA_SEGMENTS
ORDER BY BYTES DESC;""",
[],"DBA_SEGMENTS 为 DM8 兼容 Oracle 的数据字典视图。")
add("dameng","全备 / 增量（BACKUP DATABASE）","dmrman-full-incremental",
"""-- shell: DMRMAN（DM8 备份恢复工具，需先停库或按 DMRMAN 要求操作）
-- shell: dmrman CTLFILE=/dm8/data/DAMENG/dm.ini
-- DMRMAN> BACKUP DATABASE '/dm8/data/DAMENG/dm.ini' FULL BACKUPSET '/dm8/backup/full_20261124';
-- DMRMAN> BACKUP DATABASE '/dm8/data/DAMENG/dm.ini' INCREMENTAL BACKUPSET '/dm8/backup/incr_20261124';""",
[{"name":"dm.ini 路径","desc":"DM 实例配置文件路径"},{"name":"BACKUPSET","desc":"备份集目录"}],
"DMRMAN 备份命令语法需按 DM8 版本核对，备份前确认备份目录磁盘余量。")
add("dameng","闪回 / 时间点恢复","flashback-pitr",
"""-- 1. 先确认备份集与归档（只读）：
-- shell: dmrman CTLFILE=/dm8/data/DAMENG/dm.ini
-- DMRMAN> SHOW BACKUPSETS;
-- 2. 时间点恢复为危险操作，先在测试库演练：
-- DANGER: DMRMAN> RESTORE DATABASE '/dm8/data/DAMENG/dm.ini' FROM BACKUPSET '/dm8/backup/full_20261124' UNTIL TIME '2026-11-24 10:00:00';""",
[{"name":"BACKUPSET","desc":"备份集目录"},{"name":"UNTIL TIME","desc":"恢复目标时间"}],
"DMRMAN RESTORE 语法与 UNTIL 子句需在 DM8 实测核对，生产恢复前务必先停写并做副本。")
add("dameng","数据守护（DW）状态","data-watch-status",
"""SELECT TOP 20 * FROM V$DMWATCHER;""",
[],"V$DMWATCHER 的列名与返回值需在 DM8 实测核对，未部署数据守护时该视图可能无数据。")
add("dameng","DSC 集群状态","dsc-cluster-status",
"""-- shell: DMASM / DSC 集群状态以 DMASM 工具与 dmsvc 进程为准
-- shell: ps -ef | grep dmasm
-- shell: dmasm --help
SELECT NAME, INSTANCE_NAME, STATUS FROM V$INSTANCE;""",
[],
"DMASM/DSC 的状态查询方式需在 DM8 DSC 环境实测核对，不要凭印象执行集群命令。")
add("dameng","Oracle → DM 迁移检查清单","oracle-to-dm-checklist",
"""-- 迁移前检查（只读）：对象数量、数据类型、序列、存储过程
SELECT OBJECT_TYPE, COUNT(*) AS CNT FROM DBA_OBJECTS WHERE OWNER = '<SCHEMA>' GROUP BY OBJECT_TYPE ORDER BY CNT DESC;
SELECT TOP 20 TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM DBA_TAB_COLUMNS WHERE OWNER = '<SCHEMA>' AND DATA_TYPE IN ('NUMBER','VARCHAR2','CLOB','BLOB','DATE') ORDER BY TABLE_NAME;""",
[{"name":"SCHEMA","desc":"源模式名"}],
"迁移以 DM 官方 DTS 工具为准，数据类型映射（NUMBER/VARCHAR2 等）需逐项核对。")
add("dameng","兼容性检查（方言差异）","dialect-compat-check",
"""-- 检查源库中 DM 不完全兼容的写法（在 Oracle 源库或迁移评估库执行）：
SELECT TOP 20 OWNER, NAME, TYPE, LINE, TEXT FROM DBA_SOURCE
WHERE TEXT LIKE '%ROWNUM%' OR TEXT LIKE '%NVL(%' OR TEXT LIKE '%SYSDATE%'
ORDER BY OWNER, NAME, LINE;""",
[],
"DBA_SOURCE 的列名需在 DM8 实测核对，ROWNUM/NVL/SYSDATE 在 DM8 多数兼容但仍需逐项核对。")

# ================= OceanBase 4.x (16) =================
add("oceanbase","集群 / 租户 / Zone 状态","cluster-tenant-zone",
"""SELECT SVR_IP, SVR_PORT, ZONE, STATUS FROM oceanbase.__all_server ORDER BY ZONE, SVR_IP LIMIT 20;
SELECT TENANT_ID, TENANT_NAME, CREATE_TIME FROM oceanbase.__all_tenant LIMIT 20;""",
[],"MySQL 模式用以上查询，Oracle 模式需改写为对应字典视图，需在 OB 4.x 实测核对。")
add("oceanbase","资源单元（Unit）使用","unit-usage",
"""SELECT UNIT_ID, TENANT_ID, ZONE, SVR_IP, MAX_CPU, MIN_CPU, MEMORY_SIZE/1024/1024 AS MEMORY_MB, STATUS
FROM oceanbase.__all_unit
ORDER BY TENANT_ID, ZONE LIMIT 20;""",
[],"__all_unit 的内存单位与列名需在 OB 4.x 实测核对。")
add("oceanbase","租户内存 / CPU 使用","tenant-memory-cpu",
"""SELECT TENANT_ID, SVR_IP, HOLD AS MEMORY_HOLD_BYTES, USED AS MEMORY_USED_BYTES
FROM oceanbase.GV$OB_MEMORY
ORDER BY USED DESC LIMIT 20;""",
[],"GV$OB_MEMORY 的列名（HOLD/USED）需在 OB 4.x 实测核对，Oracle 模式查询方式不同。")
add("oceanbase","缓存 / 合并（Major Compaction）状态","major-compaction-status",
"""SELECT ZONE, STATUS, START_TIME FROM oceanbase.__all_zone LIMIT 20;
-- 合并进度以 OCP / obdiag 或 __all_virtual_merge_info 为准，视图名按版本不同：
-- 需在 OB 4.x 实测核对合并进度视图名后再查，不要硬编列名。""",
[],"合并进度视图名在 OB 3.x/4.x 间有变化，需在 OB 4.x 实测核对。")
add("oceanbase","Top SQL（GV$OB_SQL_AUDIT）","top-sql-audit",
"""SELECT TOP 20 SQL_ID, SQL_TEXT, ELAPSED_TIME, EXECUTIONS, ROWS_PROCESSED
FROM oceanbase.GV$OB_SQL_AUDIT
WHERE ELAPSED_TIME > 0
ORDER BY ELAPSED_TIME DESC;""".replace("TOP 20",""),
[],"MySQL 模式用 LIMIT 20，Oracle 模式用 FETCH FIRST 20 ROWS ONLY，GV$OB_SQL_AUDIT 列名需在 OB 4.x 实测核对。")
# fix OB top-sql: use LIMIT form (MySQL mode primary)
F[("oceanbase","Top SQL（GV$OB_SQL_AUDIT）")]["sql"] = """SELECT SQL_ID, SQL_TEXT, ELAPSED_TIME, EXECUTIONS
FROM oceanbase.GV$OB_SQL_AUDIT
WHERE ELAPSED_TIME > 0
ORDER BY ELAPSED_TIME DESC LIMIT 20;"""
add("oceanbase","执行计划（EXPLAIN）","explain-plan",
"""EXPLAIN SELECT * FROM <TABLE> WHERE <CONDITION>;""",
[{"name":"TABLE","desc":"表名"},{"name":"CONDITION","desc":"WHERE 条件"}],
"MySQL 模式用 EXPLAIN，Oracle 模式用 EXPLAIN PLAN FOR，需按租户模式区分。")
add("oceanbase","活跃会话 / 阻塞","active-sessions-blocking",
"""SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO
FROM oceanbase.GV$OB_PROCESSLIST
WHERE COMMAND != 'Sleep'
ORDER BY TIME DESC LIMIT 20;""",
[],"GV$OB_PROCESSLIST 列名需在 OB 4.x 实测核对，MySQL 模式与 Oracle 模式字段不同。")
add("oceanbase","杀会话（KILL）","kill-session",
"""-- 1. 先确认（只读查询）：
SELECT ID, USER, HOST, COMMAND, TIME, INFO FROM oceanbase.GV$OB_PROCESSLIST WHERE ID = <ID>;
-- 2. 确认无误后再执行（危险）：
-- DANGER: KILL <ID>;""",
[{"name":"ID","desc":"会话 ID"}],
"OB 的 KILL 语法与 MySQL 兼容，Oracle 模式需按租户模式核对，杀会话前务必确认业务影响。")
add("oceanbase","表 / 分区大小","table-partition-size",
"""SELECT TABLE_SCHEMA, TABLE_NAME, ROUND(DATA_LENGTH/1024/1024, 2) AS DATA_MB, ROUND(INDEX_LENGTH/1024/1024, 2) AS INDEX_MB, TABLE_ROWS
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA NOT IN ('information_schema','mysql','oceanbase','sys')
ORDER BY DATA_LENGTH DESC LIMIT 20;""",
[],"MySQL 模式用 INFORMATION_SCHEMA.TABLES，Oracle 模式用 DBA_SEGMENTS/DBA_TABLES，需按租户模式区分。")
add("oceanbase","磁盘使用 / 数据压缩","disk-usage-compression",
"""SELECT SVR_IP, TOTAL_SIZE/1024/1024/1024 AS TOTAL_GB, USED_SIZE/1024/1024/1024 AS USED_GB
FROM oceanbase.__all_virtual_disk_stat LIMIT 20;""",
[],"__all_virtual_disk_stat 的列名需在 OB 4.x 实测核对，如无该视图请改用 OCP 磁盘监控。")
add("oceanbase","物理备份 / 归档（OB 备份）","physical-backup",
"""-- 需先在 OCP / SQL 中配置备份目的端（OSS/NFS 等），再执行：
-- ALTER SYSTEM SET BACKUP_DEST='file:///obbackup';
-- ALTER SYSTEM BACKUP DATABASE;""",
[],
"OB 物理备份语法与备份目的端配置需在 OB 4.x 实测核对，备份前确认归档已开启。")
add("oceanbase","闪回 / 时间点恢复","flashback-pitr",
"""-- 1. 先确认备份与归档（只读）：
-- ALTER SYSTEM SHOW BACKUP STATUS;
-- 2. 时间点恢复为危险操作，先在测试租户演练：
-- DANGER: Oracle 模式：FLASHBACK TABLE <TABLE> TO TIMESTAMP TO_TIMESTAMP('2026-11-24 10:00:00','YYYY-MM-DD HH24:MI:SS');
-- DANGER: MySQL 模式无 FLASHBACK TABLE，需用备份+PITR 恢复到新租户，语法按 OB 4.x 核对。""",
[{"name":"TABLE","desc":"表名"}],
"OB 的闪回能力按租户模式差异很大，MySQL 模式不支持 Oracle 式闪回，需在 OB 4.x 实测核对。")
add("oceanbase","多副本 / Paxos 状态","replica-paxos-status",
"""SELECT LS_ID, TENANT_ID, SVR_IP, ROLE, STATUS FROM oceanbase.__all_ls ORDER BY TENANT_ID, LS_ID LIMIT 20;""",
[],"__all_ls 的列名需在 OB 4.x 实测核对，副本角色以 OCP 展示为准。")
add("oceanbase","主备切换演练","primary-standby-switchover",
"""-- 1. 先确认主备租户与日志同步（只读）：
SELECT TENANT_ID, LS_ID, SVR_IP, ROLE FROM oceanbase.__all_ls ORDER BY TENANT_ID LIMIT 20;
-- 2. 切换为危险操作，演练前停写确认：
-- DANGER: 切换命令按 OB 4.x 主备租户方案执行（OCP 切换或 ALTER SYSTEM 切换），不要直接套用 Oracle DG 命令。""",
[],
"OB 主备切换与 Oracle DG 完全不同，命令需在 OB 4.x 实测核对，演练前务必停写确认。")
add("oceanbase","MySQL → OB 迁移清单","mysql-to-ob-checklist",
"""-- 迁移前检查（只读，MySQL 模式）：
SELECT TABLE_SCHEMA, COUNT(*) AS TABLE_CNT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','mysql','sys') GROUP BY TABLE_SCHEMA ORDER BY TABLE_CNT DESC LIMIT 20;
SELECT TABLE_SCHEMA, TABLE_NAME, ENGINE FROM INFORMATION_SCHEMA.TABLES WHERE ENGINE NOT IN ('InnoDB') LIMIT 20;""",
[],
"迁移以 OMS 工具为准，存储引擎、字符集、自增列需逐项核对。")
add("oceanbase","Oracle → OB 迁移清单","oracle-to-ob-checklist",
"""-- 迁移前检查（只读，Oracle 模式）：
SELECT OWNER, OBJECT_TYPE, COUNT(*) AS CNT FROM DBA_OBJECTS GROUP BY OWNER, OBJECT_TYPE ORDER BY CNT DESC FETCH FIRST 20 ROWS ONLY;
-- 需在 OB 4.x 实测核对 DBA_OBJECTS 在 Oracle 模式下的可用性，数据类型映射以 OMS 评估报告为准。""",
[],
"迁移以 OMS 工具为准，序列、同义词、存储过程等对象需逐项核对。")

# ================= GBase 8a/8s (9) =================
add("gbase","集群节点状态（8a）","cluster-nodes-8a",
"""-- shell: gcadmin（GBase 8a 集群管理命令）
-- shell: gcadmin showcluster
-- shell: gcadmin showdistribution""",
[],"gcadmin 需在 8a 协调节点上执行，输出以 gcadmin 为准。")
add("gbase","实例状态（8s）","instance-status-8s",
"""-- shell: onstat（GBase 8s / Informix 兼容命令）
-- shell: onstat -
-- shell: onstat -g ses""",
[],"onstat 需在 8s 实例所在服务器执行，参数需按 8s 版本核对。")
add("gbase","分布键 / 数据倾斜检查（8a）","distribution-skew-8a",
"""SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema') ORDER BY TABLE_ROWS DESC LIMIT 20;
-- 分布键与倾斜详情以 8a 的分布信息表为准，系统表名按版本不同，需在 8a 实测核对，不要硬编。""",
[],"8a 分布信息系统表名需在 8a 实测核对，本条只给通用表大小查询。")
add("gbase","统计信息 / 优化器","analyze-stats",
"""SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS, UPDATE_TIME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema') ORDER BY UPDATE_TIME ASC LIMIT 20;
-- 如需收集统计信息（建议非高峰）：
-- ANALYZE TABLE <SCHEMA>.<TABLE>;""",
[{"name":"SCHEMA.TABLE","desc":"表名"}],
"8a 的统计信息收集语法需在 8a 实测核对，ANALYZE 模板仅供参考。")
add("gbase","慢SQL Top","slow-sql-top",
"""-- 8a/8s 的慢 SQL 以慢查询日志与系统表为准，系统表名按版本不同：
-- shell: 查看 8a 慢查询日志路径与配置（gbase 配置文件），再用文本工具分析
-- 需在 8a/8s 实测核对慢 SQL 系统表名后再填具体查询，不要硬编。""",
[],"8a/8s 慢 SQL 系统表名需在 8a/8s 实测核对，本条暂不编造系统表。")
add("gbase","执行计划","explain-plan",
"""EXPLAIN SELECT * FROM <TABLE> WHERE <CONDITION>;""",
[{"name":"TABLE","desc":"表名"},{"name":"CONDITION","desc":"WHERE 条件"}],
"8a 与 8s 的 EXPLAIN 输出格式不同，需按版本核对。")
add("gbase","8a 备份（gcbackup）","gcbackup-8a",
"""-- shell: gcbackup（GBase 8a 集群备份，需在协调节点执行）
-- shell: gcbackup -h
-- shell: gcbackup <备份目录>""",
[{"name":"备份目录","desc":"备份目标目录"}],
"gcbackup 参数需在 8a 实测核对，备份前确认磁盘余量与集群状态。")
add("gbase","8s 逻辑备份（dbexport）","dbexport-8s",
"""-- shell: dbexport（GBase 8s / Informix 兼容逻辑备份）
-- shell: dbexport -d <DATABASE> -o <备份目录>""",
[{"name":"DATABASE","desc":"数据库名"},{"name":"备份目录","desc":"备份目标目录"}],
"dbexport 参数需在 8s 实测核对，备份前确认磁盘余量。")
add("gbase","Oracle/MySQL → GBase 迁移清单","oracle-mysql-to-gbase-checklist",
"""-- 迁移前检查（只读，通用）：
SELECT TABLE_SCHEMA, COUNT(*) AS TABLE_CNT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema','mysql','sys') GROUP BY TABLE_SCHEMA ORDER BY TABLE_CNT DESC LIMIT 20;
-- 数据类型映射、分布键选择、字符集需以 GBase 迁移工具评估报告为准。""",
[],
"迁移工具与类型映射需按 8a/8s 版本核对，分布键选择是 8a 迁移的关键。")

# ================= TiDB (10) =================
add("tidb","集群状态（tiup cluster display）","tiup-cluster-display",
"""-- shell: tiup cluster display <CLUSTER_NAME>
-- shell: tiup cluster display <CLUSTER_NAME> --uptime""",
[{"name":"CLUSTER_NAME","desc":"集群名"}],
"tiup 需在中控机执行，集群状态以 tiup 输出与 Dashboard 为准。")
add("tidb","TiKV / PD 状态","tikv-pd-status",
"""SELECT TYPE, INSTANCE, STATUS, START_TIME FROM INFORMATION_SCHEMA.CLUSTER_INFO ORDER BY TYPE, INSTANCE LIMIT 20;
-- shell: pd-ctl -u http://<PD_IP>:2379 store""",
[{"name":"PD_IP","desc":"PD 地址"}],
"TiKV/PD 详细状态以 Dashboard 与 pd-ctl 为准，CLUSTER_INFO 列名需在 TiDB 6.x+ 实测核对。")
add("tidb","热点 Region 检查","hot-regions",
"""SELECT REGION_ID, TABLE_ID, INDEX_ID, APPROXIMATE_SIZE, APPROXIMATE_KEYS FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS ORDER BY APPROXIMATE_SIZE DESC LIMIT 20;""",
[],"TIKV_REGION_STATUS 的列名需在 TiDB 6.x+ 实测核对，热点以 Dashboard 热点图为准。")
add("tidb","统计信息 / ANALYZE","analyze-table",
"""-- 先确认表与统计信息时间（只读）：
SELECT TABLE_SCHEMA, TABLE_NAME, UPDATE_TIME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '<SCHEMA>' ORDER BY UPDATE_TIME ASC LIMIT 20;
-- 收集统计信息（建议非高峰）：
-- ANALYZE TABLE <SCHEMA>.<TABLE>;""",
[{"name":"SCHEMA.TABLE","desc":"表名"}],
"TiDB 的 ANALYZE 与 MySQL 兼容，生产建议非高峰执行。")
add("tidb","慢查询日志 / Top SQL（Dashboard）","slow-query-top",
"""SELECT QUERY, QUERY_TIME, MEM_MAX, TIME FROM INFORMATION_SCHEMA.SLOW_QUERY WHERE QUERY_TIME > 1 ORDER BY QUERY_TIME DESC LIMIT 20;""",
[],"SLOW_QUERY 需开启慢查询日志，字段名需在 TiDB 6.x+ 实测核对。")
add("tidb","EXPLAIN ANALYZE","explain-analyze",
"""EXPLAIN ANALYZE SELECT * FROM <TABLE> WHERE <CONDITION>;""",
[{"name":"TABLE","desc":"表名"},{"name":"CONDITION","desc":"WHERE 条件"}],
"TiDB 的 EXPLAIN ANALYZE 与 MySQL 8.0 类似，输出含各算子真实耗时。")
add("tidb","多副本 / Raft 状态","replica-raft-status",
"""SELECT STORE_ID, ADDRESS, STATE, REGION_COUNT, LEADER_COUNT FROM INFORMATION_SCHEMA.TIKV_STORE_STATUS ORDER BY STORE_ID LIMIT 20;""",
[],"TIKV_STORE_STATUS 的列名需在 TiDB 6.x+ 实测核对，副本详情以 PD/Dashboard 为准。")
add("tidb","TiFlash 同步延迟","tiflash-replica-lag",
"""SELECT TABLE_SCHEMA, TABLE_NAME, REPLICA_COUNT, AVAILABLE, PROGRESS FROM INFORMATION_SCHEMA.TIFLASH_REPLICA ORDER BY PROGRESS ASC LIMIT 20;""",
[],"TIFLASH_REPLICA 的列名需在 TiDB 6.x+ 实测核对，PROGRESS<1 表示同步中。")
add("tidb","BR 全备 / PITR","br-backup-pitr",
"""-- shell: br（TiDB 备份恢复工具，需配置存储目的端）
-- shell: br backup full --pd "http://<PD_IP>:2379" --storage "s3://<BUCKET>/<PATH>" --log-file /tmp/br.log
-- shell: br restore full --pd "http://<PD_IP>:2379" --storage "s3://<BUCKET>/<PATH>" --log-file /tmp/br-restore.log""",
[{"name":"PD_IP","desc":"PD 地址"},{"name":"BUCKET/PATH","desc":"备份存储路径"}],
"BR 备份/PITR 语法与存储配置需在 TiDB 6.x+ 实测核对，恢复前先在测试集群演练。")
add("tidb","Dumpling 逻辑备份","dumpling-backup",
"""-- shell: dumpling（TiDB 逻辑导出工具）
-- shell: dumpling -u root -P 4000 -h <TIDB_IP> -o /tmp/dumpling_out --filetype sql""",
[{"name":"TIDB_IP","desc":"TiDB 地址"},{"name":"输出目录","desc":"导出目录"}],
"dumpling 参数需在 TiDB 6.x+ 实测核对，大库优先用 BR 物理备份。")

# ================= 通用 / 跨库 (11) =================
add("common","SQL 格式化（Oracle/MySQL/PG/SQL Server）","sql-format",
"见插件内置：lib/sql-core.js formatSql",
[],"v0.1 插件已实现，本地运行不联网，见 lib/sql-core.js。")
add("common","方言互转 Oracle↔MySQL","dialect-convert",
"见插件内置：lib/sql-core.js convertDialect",
[],"v0.1 插件已实现，规则式互转非完整转译，上线前需在测试库跑一遍。")
add("common","SQL 脱敏","sql-desensitize",
"见插件内置：lib/sql-core.js desensitizeSql",
[],"v0.1 插件已实现，字符串→***、数字→?。")
add("common","列表转 IN / 批量 INSERT","list-to-in",
"见插件内置：lib/sql-core.js listToIn",
[],"v0.1 插件已实现，Oracle IN 超 1000 个会报 ORA-01795。")
add("common","时间戳互转","timestamp-convert",
"见插件内置：lib/sql-core.js timestampConvert",
[],"v0.1 插件已实现，10 位秒/13 位毫秒与日期互转。")
add("common","连接串速查（JDBC / ODBC）","connection-strings",
"""-- Oracle: jdbc:oracle:thin:@<HOST>:1521/<SERVICE>
-- MySQL/TiDB: jdbc:mysql://<HOST>:3306/<DB>?useSSL=false&serverTimezone=Asia/Shanghai
-- PostgreSQL: jdbc:postgresql://<HOST>:5432/<DB>
-- SQL Server: jdbc:sqlserver://<HOST>:1433;databaseName=<DB>
-- 达梦 DM8: jdbc:dm://<HOST>:5236/<DB>
-- OceanBase MySQL 模式: jdbc:mysql://<HOST>:2883/<DB>
-- GBase 8a: jdbc:mysql://<HOST>:5258/<DB>""",
[{"name":"HOST/DB","desc":"地址与库名"}],
"端口与驱动名需按实际版本核对，连接串不要写真实密码。")
add("common","端口 / 连通性检查","port-connectivity",
"""-- shell: Windows
-- shell: Test-NetConnection -ComputerName <HOST> -Port <PORT>
-- shell: Linux/macOS
-- shell: nc -zv <HOST> <PORT>
-- shell: telnet <HOST> <PORT>""",
[{"name":"HOST","desc":"地址"},{"name":"PORT","desc":"端口"}],
"常用端口：Oracle 1521、MySQL/TiDB 3306/4000、PG 5432、SQL Server 1433、DM 5236、OB 2883、Redis 6379。")
add("common","字符集 / 时区检查","charset-timezone",
"""-- Oracle: SELECT * FROM NLS_DATABASE_PARAMETERS WHERE PARAMETER IN ('NLS_CHARACTERSET','NLS_NCHAR_CHARACTERSET');
-- MySQL: SHOW VARIABLES LIKE 'character_set%'; SHOW VARIABLES LIKE 'time_zone';
-- PostgreSQL: SHOW server_encoding; SHOW timezone;
-- SQL Server: SELECT SERVERPROPERTY('Collation');
-- 达梦: SELECT * FROM V$PARAMETER WHERE NAME LIKE '%CHARSET%';
-- TiDB: SHOW VARIABLES LIKE 'character_set%';""",
[],
"各库字符集查询语法不同，达梦条需在 DM8 实测核对。")
add("common","Redis 常用命令（INFO / SLOWLOG / 内存）","redis-commands",
"""-- shell: redis-cli -h <HOST> -p 6379 INFO memory
-- shell: redis-cli -h <HOST> -p 6379 SLOWLOG GET 10""",
[{"name":"HOST","desc":"Redis 地址"}],
"二期，Redis 6.x/7.x 示例命令，需按版本核对。")
add("common","MongoDB 慢查询 / 索引","mongodb-slow-index",
"""// MongoDB shell:
db.currentOp({ "active": true, "secs_running": { "$gt": 5 } });
db.<COLLECTION>.getIndexes();""",
[{"name":"COLLECTION","desc":"集合名"}],
"二期，MongoDB 6.x/7.x 示例命令，需按版本核对。")
add("common","SQLite 常用命令","sqlite-commands",
"""-- shell: sqlite3 <DB_FILE>.db
-- sqlite> .tables
-- sqlite> PRAGMA table_info(<TABLE>);""",
[{"name":"DB_FILE/TABLE","desc":"库文件与表名"}],
"二期，SQLite 3.x 示例命令，需按版本核对。")

# ================= build =================
def sanitize_cat(name):
    return name.replace(" / ", "-").replace("/", "-").replace(" ", "")
def slugify(s):
    return s
TARGETS = ["dameng","oceanbase","gbase","tidb","common"]
for db_id in TARGETS:
    db = DBS[db_id]
    # deep copy via json round-trip
    db_copy = json.loads(json.dumps(db, ensure_ascii=False))
    total = 0
    for cat in db_copy["categories"]:
        cat_dir = sanitize_cat(cat["name"])
        for sub in cat["subcategories"]:
            for idx, item in enumerate(sub["items"], start=1):
                key = (db_id, item["title"])
                assert key in F, f"MISSING FILL {key}"
                fill = F[key]
                item["sql"] = fill["sql"]
                item["params"] = fill["params"]
                item["notes"] = fill["notes"]
                total += 1
                # .sql file
                outdir = ROOT / "scripts" / db_id / cat_dir
                outdir.mkdir(parents=True, exist_ok=True)
                fname = f"{idx:02d}-{fill['slug']}.sql"
                header = (f"-- {item['title']}\n-- 适用版本：{item['versions']}\n-- 风险：{item['risk']}\n"
                          f"-- 说明：{item['desc']}\n-- 备注：{item['notes']}\n\n")
                (outdir / fname).write_text(header + fill["sql"].rstrip() + "\n", encoding="utf-8")
    out_json = ROOT / "data" / f"toolbox-{db_id}.json"
    out_json.write_text(json.dumps(db_copy, ensure_ascii=False, indent=2), encoding="utf-8")
    print(db_id, total, out_json)
print("DONE total", sum(1 for k in F if k[0] in TARGETS))
