# -*- coding: utf-8 -*-
"""生成金仓 KingBaseES 与崖山 YashanDB 各 14 条脚本。
依据：金仓 help.kingbase.com.cn 官方文档（V9）与 kingbase.com.cn 技术文章；
崖山 YashanDB 管理员手册 v23.2.2.0 / 参考手册 v23.2.2.0 与 Oracle 兼容视图清单。
未在真实环境跑过，列名只按手册推断的条目 notes 均标“需在 XX 版本实测核对”。
只写新文件，不改动已有文件。
"""
import json, os

BASE = os.path.expanduser("~/workspace/utools-dba-sql")
KB_URL = "https://help.kingbase.com.cn/"
YS_URL = "https://doc.yashandb.com/"

def item(title, versions, risk, desc, sql, params, notes, id_):
    return {"title": title, "versions": versions, "risk": risk, "desc": desc,
            "sql": sql, "params": params, "notes": notes, "id": id_}

# ================= 金仓 KingBaseES =================
kb = [
 # 日常巡检 / 实例
 item("实例状态 / 版本", "V9+", "只读", "version(), sys_stat_activity",
      "SELECT version() AS version;\nSELECT count(*) AS session_count FROM sys_stat_activity;\nSELECT state, count(*) AS cnt FROM sys_stat_activity GROUP BY state ORDER BY cnt DESC;",
      [], "依据：金仓官方文档中心 " + KB_URL + "（KingbaseES V9）；version() 与 sys_stat_activity（pid/state/query/wait_event_type）见 kingbase.com.cn 性能视图文章。sys_stat_activity 的 sys_ 前缀为 KES V9 命名，pg_stat_activity 为 PG 原生命名，二者同义。未在真实环境跑过，需在 KES V9 实测核对。",
      "kingbase-001"),
 item("无效对象清单", "V9+", "只读", "DBA_OBJECTS（Oracle 兼容模式）",
      "SELECT OWNER, OBJECT_NAME, OBJECT_TYPE, STATUS\nFROM DBA_OBJECTS\nWHERE STATUS = 'INVALID'\nORDER BY OWNER, OBJECT_TYPE, OBJECT_NAME;",
      [], "依据：金仓官方文档中心 " + KB_URL + "。仅 Oracle 兼容模式提供 DBA_OBJECTS，PG 兼容模式无此视图；DBA_OBJECTS 列名与 STATUS 取值需在 KES V9 Oracle 兼容模式实测核对。",
      "kingbase-002"),
 # 性能优化 / 参数与缓存
 item("缓存命中率 / 内存", "V9+", "只读", "sys_stat_database",
      "SELECT datname, blks_hit, blks_read,\n  ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS hit_ratio_pct\nFROM sys_stat_database\nORDER BY datname;",
      [], "依据：kingbase.com.cn 性能视图文章（sys_stat_database：事务数、块读写数）与 PG 兼容的 sys_stat_database 列名。blks_hit/blks_read 列名需在 KES V9 实测核对。",
      "kingbase-003"),
 item("统计信息收集", "V9+", "谨慎", "ANALYZE",
      "-- 1. 先确认表上次分析时间（只读）：\nSELECT schemaname, relname, last_analyze, last_autoanalyze, n_live_tup\nFROM sys_stat_user_tables\nWHERE schemaname = '<SCHEMA>' AND relname = '<TABLE>';\n-- 2. 确认后在非高峰执行（谨慎）：\n-- DANGER: ANALYZE <SCHEMA>.<TABLE>;",
      [{"name": "SCHEMA", "desc": "模式名"}, {"name": "TABLE", "desc": "表名"}],
      "依据：kingbase.com.cn 性能视图文章（sys_stat_user_tables 的 last_analyze / n_live_tup 用于判断是否需 ANALYZE/VACUUM）与 PG 兼容语法。ANALYZE 语法按 PG 兼容模式，需在 KES V9 实测核对。",
      "kingbase-004"),
 # 慢SQL / 定位
 item("慢SQL Top（sys_stat_statements）", "V9+", "只读", "sys_stat_statements",
      "SELECT query, calls, total_time, mean_time, rows, shared_blks_hit, shared_blks_read\nFROM sys_stat_statements\nORDER BY total_time DESC\nLIMIT 10;",
      [], "依据：kingbase.com.cn《KES 如何配置 sys_stat_statements》与性能调优白皮书：需 kingbase.conf 配 shared_preload_libraries='sys_stat_statements' 并重启，再 CREATE EXTENSION sys_stat_statements；列 query/calls/total_time/mean_time/rows/shared_blks_hit/shared_blks_read 见该文。未启用扩展时视图无数据，需在 KES V9 实测核对。",
      "kingbase-005"),
 item("执行计划（EXPLAIN ANALYZE）", "V9+", "只读", "EXPLAIN ANALYZE",
      "EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM <SCHEMA>.<TABLE> WHERE <CONDITION>;",
      [{"name": "SCHEMA.TABLE", "desc": "表名"}, {"name": "CONDITION", "desc": "WHERE 条件"}],
      "依据：金仓官方文档中心 " + KB_URL + "（PG 兼容语法）。注意 EXPLAIN ANALYZE 会真实执行 SQL，写操作改用不带 ANALYZE 的 EXPLAIN；输出格式需在 KES V9 实测核对。",
      "kingbase-006"),
 # 锁 / 会话 / 锁
 item("阻塞锁 / 会话", "V9+", "只读", "sys_locks / sys_stat_activity",
      "SELECT blocked.pid AS blocked_pid, blocked.query AS blocked_query,\n  blocking.pid AS blocking_pid, blocking.query AS blocking_query,\n  blocked.wait_event_type, blocked.wait_event\nFROM sys_locks blocked_locks\nJOIN sys_stat_activity blocked ON blocked.pid = blocked_locks.pid\nJOIN sys_locks blocking_locks\n  ON blocking_locks.locktype = blocked_locks.locktype\n  AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database\n  AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation\n  AND blocking_locks.pid != blocked_locks.pid\nJOIN sys_stat_activity blocking ON blocking.pid = blocking_locks.pid\nWHERE NOT blocked_locks.granted;",
      [], "依据：kingbase.com.cn 性能视图文章（sys_locks 视图 + sys_stat_activity 关联分析阻塞链，wait_event_type='Lock' 为瓶颈信号）。查询结构为 PG 标准阻塞查询的 sys_ 前缀写法，sys_locks 列名（locktype/relation/granted）需在 KES V9 实测核对；pg_locks/pg_stat_activity 为 PG 原生命名。",
      "kingbase-007"),
 item("杀会话", "V9+", "危险", "pg_terminate_backend",
      "-- 1. 先确认（只读查询）：\nSELECT pid, usename, datname, state, query_start, query FROM sys_stat_activity WHERE pid = <PID>;\n-- 2. 确认无误后再执行（危险）：\n-- DANGER: SELECT pg_terminate_backend(<PID>);",
      [{"name": "PID", "desc": "会话进程 ID"}],
      "依据：金仓官方文档中心 " + KB_URL + "（PG 兼容函数）。pg_terminate_backend 为 PG 兼容函数名，需在 KES V9 实测核对；杀会话前务必确认业务影响，优先用 pg_cancel_backend 取消当前查询。",
      "kingbase-008"),
 # 空间 / 空间
 item("表空间大小一览", "V9+", "只读", "sys_tablespace / sys_tablespace_size",
      "SELECT spcname, sys_size_pretty(sys_tablespace_size(spcname)) AS size\nFROM sys_tablespace\nORDER BY sys_tablespace_size(spcname) DESC;",
      [], "依据：金仓运维命令清单（sys_tablespace + sys_tablespace_size）与官方文档中心 " + KB_URL + "。KES 未提供 DBA_FREE_SPACE 式空闲视图，本条只给各表空间已用大小，使用率需结合操作系统 df 或数据目录大小估算，需在 KES V9 实测核对。",
      "kingbase-009"),
 item("大表 Top", "V9+", "只读", "sys_total_relation_size",
      "SELECT relname, sys_size_pretty(sys_total_relation_size(oid)) AS total_size\nFROM sys_class\nWHERE relkind = 'r'\nORDER BY sys_total_relation_size(oid) DESC\nLIMIT 20;",
      [], "依据：金仓运维命令清单（sys_total_relation_size + sys_class relkind='r'）与官方文档中心 " + KB_URL + "。sys_total_relation_size 含表 + 索引 + TOAST，需在 KES V9 实测核对。",
      "kingbase-010"),
 # 备份恢复 / 备份
 item("物理备份（sys_rman 全量 / 增量）", "V9+", "谨慎", "sys_rman",
      "-- shell: sys_rman 物理备份（需先完成备份仓库初始化）\n-- shell: sys_rman init -D <数据目录> -R <备份仓库目录>\n-- shell: sys_rman backup -D <数据目录> -R <备份仓库目录> -t full\n-- shell: sys_rman backup -D <数据目录> -R <备份仓库目录> -t incr",
      [{"name": "数据目录", "desc": "实例数据目录路径"}, {"name": "备份仓库目录", "desc": "sys_rman 备份仓库 repo_path"}],
      "依据：kingbase.com.cn《金仓数据库备份恢复：从原理到实战》（sys_rman init/backup -t full/-t incr，关键参数 repo_path/stanza_name/compress_type）与官方文档中心 " + KB_URL + "。备份前确认归档已开启（archive_mode=on）与仓库磁盘余量；具体参数需按 KES V9 手册核对，需在 KES V9 实测核对。",
      "kingbase-011"),
 item("时间点恢复演练清单", "V9+", "危险", "sys_rman restore / PITR",
      "-- 1. 先确认归档与备份（只读）：\nSHOW archive_mode;\nSELECT * FROM sys_stat_archiver;\n-- 2. 恢复为危险操作，先停库、先在测试库全流程演练：\n-- DANGER: sys_rman restore -D <数据目录> -R <备份仓库目录>\n-- DANGER: 恢复后按手册用 WAL 归档做时间点恢复（PITR），切勿在生产库直接演练。",
      [{"name": "数据目录", "desc": "实例数据目录路径"}, {"name": "备份仓库目录", "desc": "sys_rman 备份仓库 repo_path"}],
      "依据：kingbase.com.cn《金仓数据库备份恢复：从原理到实战》（恢复前停库、sys_rman restore、结合 WAL 做 PITR）与官方文档中心 " + KB_URL + "。restore 的完整参数与 PITR 步骤需按 KES V9 手册核对，未在真实环境跑过，需在 KES V9 实测核对。",
      "kingbase-012"),
 # 高可用 / 流复制
 item("主备 / 流复制状态", "V9+", "只读", "sys_stat_replication",
      "SELECT application_name, client_addr, state, sync_state,\n  sent_lsn, write_lsn, flush_lsn, replay_lsn\nFROM sys_stat_replication;\n-- 备库延迟（在备库执行）：\n-- SELECT now() - pg_last_xact_replay_timestamp() AS replay_delay;",
      [], "依据：金仓官方文档中心 " + KB_URL + "（PG 兼容的流复制视图）。sys_stat_replication 列名（sent_lsn/write_lsn/flush_lsn/replay_lsn）与备库函数 pg_last_xact_replay_timestamp 需在 KES V9 实测核对；pg_stat_replication 为 PG 原生命名。",
      "kingbase-013"),
 # 用户 / 安全 / 账号
 item("用户与角色列表", "V9+", "只读", "pg_roles",
      "SELECT rolname, rolsuper, rolcanlogin, rolconnlimit\nFROM pg_roles\nORDER BY rolname;",
      [], "依据：金仓官方文档中心 " + KB_URL + "（PG 兼容模式系统目录）。pg_roles 列名需在 KES V9 实测核对；Oracle 兼容模式下用户查询改用 DBA_USERS，两种模式不可混用。",
      "kingbase-014"),
]

# ================= 崖山 YashanDB =================
ys = [
 # 日常巡检 / 实例
 item("实例状态 / 版本", "23.2+", "只读", "V$INSTANCE, V$VERSION",
      "SELECT * FROM V$INSTANCE;\nSELECT * FROM V$VERSION;",
      [], "依据：YashanDB 管理员手册 v23.2.2.0（SELECT status FROM V$INSTANCE；实例启停章节）与官方文档中心 " + YS_URL + "。V$INSTANCE/V$VERSION 列名以手册为准，SELECT * 避免编列名；需在 YashanDB 23.2 实测核对。",
      "yashandb-001"),
 item("无效对象清单", "23.2+", "只读", "DBA_OBJECTS",
      "SELECT OWNER, OBJECT_NAME, OBJECT_TYPE, STATUS\nFROM DBA_OBJECTS\nWHERE STATUS = 'INVALID'\nORDER BY OWNER, OBJECT_TYPE, OBJECT_NAME;",
      [], "依据：YashanDB 与 Oracle 兼容性说明（DBA_OBJECTS 属 Oracle 兼容 DBA 视图清单）与官方文档中心 " + YS_URL + "。DBA_OBJECTS 在 YashanDB 中的列名与 STATUS 取值需在 YashanDB 23.2 实测核对。",
      "yashandb-002"),
 # 性能优化 / 性能
 item("缓存命中率 / 内存", "23.2+", "只读", "V$SYSSTAT",
      "SELECT NAME, VALUE FROM V$SYSSTAT\nWHERE NAME LIKE '%physical reads%' OR NAME LIKE '%consistent gets%' OR NAME LIKE '%db block gets%';\n-- 命中率估算：1 - physical reads / (consistent gets + db block gets)，分母为 0 时结果为 NULL。",
      [], "依据：YashanDB 与 Oracle 兼容性说明（V$SYSSTAT 属 Oracle 兼容动态视图清单）与官方文档中心 " + YS_URL + "。V$SYSSTAT 统计项名称为 Oracle 兼容命名，需在 YashanDB 23.2 实测核对；精确列名未在手册检索中逐项确认，故用 LIKE 匹配。",
      "yashandb-003"),
 item("统计信息收集", "23.2+", "谨慎", "DBMS_STATS",
      "-- 1. 先确认表上次分析时间（只读）：\nSELECT OWNER, TABLE_NAME, NUM_ROWS, LAST_ANALYZED FROM DBA_TABLES\nWHERE OWNER = '<SCHEMA>' AND TABLE_NAME = '<TABLE>';\n-- 2. 确认后在非高峰执行（谨慎）：\n-- DANGER: EXEC DBMS_STATS.GATHER_TABLE_STATS('<SCHEMA>', '<TABLE>');",
      [{"name": "SCHEMA", "desc": "模式名"}, {"name": "TABLE", "desc": "表名"}],
      "依据：YashanDB 与 Oracle 兼容性说明（Oracle 兼容语法与 DBA_TABLES 视图）与官方文档中心 " + YS_URL + "。DBMS_STATS.GATHER_TABLE_STATS 在 YashanDB 中的可用性与参数需在 YashanDB 23.2 实测核对。",
      "yashandb-004"),
 # 慢SQL / 定位
 item("慢SQL Top（V$SQL）", "23.2+", "只读", "V$SQL",
      "SELECT * FROM (\n  SELECT SQL_TEXT, ELAPSED_TIME, EXECUTIONS\n  FROM V$SQL\n  WHERE ELAPSED_TIME > 0\n  ORDER BY ELAPSED_TIME DESC\n) WHERE ROWNUM <= 20;",
      [], "依据：YashanDB 与 Oracle 兼容性说明（V$SQL 属 Oracle 兼容动态视图清单）与官方文档中心 " + YS_URL + "。V$SQL 列名（SQL_TEXT/ELAPSED_TIME/EXECUTIONS）为 Oracle 兼容命名，需在 YashanDB 23.2 实测核对。",
      "yashandb-005"),
 item("执行计划（EXPLAIN PLAN）", "23.2+", "只读", "EXPLAIN PLAN / DBMS_XPLAN",
      "EXPLAIN PLAN FOR SELECT * FROM <SCHEMA>.<TABLE> WHERE <CONDITION>;\nSELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);",
      [{"name": "SCHEMA.TABLE", "desc": "表名"}, {"name": "CONDITION", "desc": "WHERE 条件"}],
      "依据：YashanDB 与 Oracle 兼容性说明（Oracle 兼容 SQL 语法）与官方文档中心 " + YS_URL + "。DBMS_XPLAN.DISPLAY 在 YashanDB 中的可用性需在 YashanDB 23.2 实测核对；EXPLAIN PLAN 本身不执行 SQL。",
      "yashandb-006"),
 # 锁 / 会话 / 锁
 item("阻塞锁 / 会话", "23.2+", "只读", "V$LOCKED_OBJECT / V$SESSION",
      "SELECT S.SID, S.SERIAL#, S.USERNAME, S.STATUS, O.OBJECT_NAME, L.LOCKED_MODE\nFROM V$LOCKED_OBJECT L\nJOIN DBA_OBJECTS O ON L.OBJECT_ID = O.OBJECT_ID\nJOIN V$SESSION S ON L.SESSION_ID = S.SID\nORDER BY S.SID;",
      [], "依据：YashanDB 与 Oracle 兼容性说明（V$LOCKED_OBJECT、V$SESSION、V$LOCK 属 Oracle 兼容动态视图清单）与官方文档中心 " + YS_URL + "。V$LOCKED_OBJECT 列名（SESSION_ID/OBJECT_ID/LOCKED_MODE）与 V$SESSION 列名（SID/SERIAL#/USERNAME/STATUS）为 Oracle 兼容命名，需在 YashanDB 23.2 实测核对。",
      "yashandb-007"),
 item("杀会话", "23.2+", "危险", "ALTER SYSTEM KILL SESSION",
      "-- 1. 先确认（只读查询）：\nSELECT SID, SERIAL#, USERNAME, STATUS, MACHINE FROM V$SESSION WHERE SID = <SID>;\n-- 2. 确认无误后再执行（危险）：\n-- DANGER: ALTER SYSTEM KILL SESSION '<SID>,<SERIAL#>';",
      [{"name": "SID", "desc": "会话 SID"}, {"name": "SERIAL#", "desc": "会话 SERIAL#"}],
      "依据：YashanDB 与 Oracle 兼容性说明（V$SESSION 列 SID/SERIAL#，Oracle 兼容语法）与官方文档中心 " + YS_URL + "。ALTER SYSTEM KILL SESSION 语法为 Oracle 兼容写法，需在 YashanDB 23.2 实测核对；杀会话前务必确认业务影响。",
      "yashandb-008"),
 # 空间 / 空间
 item("表空间使用率", "23.2+", "只读", "DBA_DATA_FILES / DBA_FREE_SPACE",
      "SELECT T.TABLESPACE_NAME, ROUND(SUM(F.BYTES)/1024/1024, 2) AS TOTAL_MB,\n  ROUND((SUM(F.BYTES) - NVL(SUM(FREE.BYTES), 0))/1024/1024, 2) AS USED_MB,\n  ROUND((1 - NVL(SUM(FREE.BYTES), 0)/SUM(F.BYTES)) * 100, 2) AS USED_PCT\nFROM DBA_DATA_FILES F\nJOIN DBA_TABLESPACES T ON F.TABLESPACE_NAME = T.TABLESPACE_NAME\nLEFT JOIN (SELECT TABLESPACE_NAME, SUM(BYTES) BYTES FROM DBA_FREE_SPACE GROUP BY TABLESPACE_NAME) FREE\n  ON FREE.TABLESPACE_NAME = T.TABLESPACE_NAME\nGROUP BY T.TABLESPACE_NAME\nORDER BY USED_PCT DESC;",
      [], "依据：YashanDB 与 Oracle 兼容性说明（DBA_TABLESPACES/DBA_DATA_FILES 属 Oracle 兼容 DBA 视图清单）与官方文档中心 " + YS_URL + "。DBA_FREE_SPACE 列名需在 YashanDB 23.2 实测核对；>85% 预警。空闲字节用 SUM 聚合，避免重复计算。",
      "yashandb-009"),
 item("大表 Top", "23.2+", "只读", "DBA_SEGMENTS",
      "SELECT * FROM (\n  SELECT OWNER, SEGMENT_NAME, SEGMENT_TYPE, ROUND(BYTES/1024/1024, 2) AS SIZE_MB\n  FROM DBA_SEGMENTS\n  ORDER BY BYTES DESC\n) WHERE ROWNUM <= 20;",
      [], "依据：YashanDB 与 Oracle 兼容性说明（Oracle 兼容 DBA 视图）与官方文档中心 " + YS_URL + "。DBA_SEGMENTS 列名（OWNER/SEGMENT_NAME/SEGMENT_TYPE/BYTES）为 Oracle 兼容命名，需在 YashanDB 23.2 实测核对。",
      "yashandb-010"),
 # 备份恢复 / 备份
 item("备份 / 归档状态", "23.2+", "只读", "V$DATABASE / V$ARCHIVED_LOG",
      "SELECT DATABASE_NAME, LOG_MODE, OPEN_MODE FROM V$DATABASE;\nSELECT * FROM (\n  SELECT SEQUENCE#, FIRST_TIME, ARCHIVED\n  FROM V$ARCHIVED_LOG\n  WHERE FIRST_TIME > SYSDATE - 1\n  ORDER BY FIRST_TIME DESC\n) WHERE ROWNUM <= 20;",
      [], "依据：YashanDB 管理员手册 v23.2.2.0（V$DATABASE 的 log_mode 字段表示归档模式，ARCHIVELOG/NOARCHIVELOG；默认归档路径由 ARCHIVE_LOCAL_DEST 控制）与官方文档中心 " + YS_URL + "。V$ARCHIVED_LOG 属 Oracle 兼容动态视图清单，列名（SEQUENCE#/FIRST_TIME/ARCHIVED）需在 YashanDB 23.2 实测核对。",
      "yashandb-011"),
 item("时间点恢复演练清单", "23.2+", "危险", "PITR 演练",
      "-- 恢复演练清单（只读检查 + 演练步骤，恢复命令以官方手册为准，禁止凭印象执行）：\n-- 1. 确认归档模式（只读）：\nSELECT DATABASE_NAME, LOG_MODE, OPEN_MODE FROM V$DATABASE;\n-- 2. 确认归档连续性（只读）：\nSELECT SEQUENCE#, FIRST_TIME FROM V$ARCHIVED_LOG WHERE FIRST_TIME > SYSDATE - 7 ORDER BY SEQUENCE#;\n-- 3. 确认最近备份集可用（按管理员手册的备份集管理方式核对）；\n-- DANGER: 恢复命令（工具名与参数）需按 YashanDB 管理员手册核对，先在测试库全流程演练，生产恢复前先停写并做副本。",
      [{"name": "恢复目标时间", "desc": "PITR 目标时间点"}],
      "依据：YashanDB 管理员手册 v23.2.2.0（归档模式 + redo 归档支持 PITR；故障恢复靠历史全量备份 + 归档 redo 重做）与官方文档中心 " + YS_URL + "。备份恢复工具的具体命令名与参数未在本次官方手册检索中逐项确认，故本条只给清单、不编命令，需在 YashanDB 23.2 实测核对。",
      "yashandb-012"),
 # 高可用 / 主备
 item("主备状态 / 复制延迟", "23.2+", "只读", "V$DATABASE / V$ARCHIVE_DEST_STATUS",
      "SELECT DATABASE_NAME, LOG_MODE, OPEN_MODE, PROTECTION_MODE, DATABASE_ROLE, BLOCK_SIZE, STATUS FROM V$DATABASE;\nSELECT DEST_ID, STATUS, TYPE, ERROR FROM V$ARCHIVE_DEST_STATUS;",
      [], "依据：YashanDB 管理员手册 v23.2.2.0（V$DATABASE 的 DATABASE_ROLE/PROTECTION_MODE 字段示例，主备模式必看）与 Oracle 兼容性说明（V$ARCHIVE_DEST、V$ARCHIVE_DEST_STATUS、V$ARCHIVE_GAP 属兼容动态视图清单），官方文档中心 " + YS_URL + "。V$ARCHIVE_DEST_STATUS 列名（DEST_ID/STATUS/TYPE/ERROR）为 Oracle 兼容命名，需在 YashanDB 23.2 实测核对。",
      "yashandb-013"),
 # 用户 / 安全 / 账号
 item("用户列表与权限", "23.2+", "只读", "DBA_USERS / DBA_SYS_PRIVS",
      "SELECT USERNAME, ACCOUNT_STATUS, DEFAULT_TABLESPACE, CREATED FROM DBA_USERS ORDER BY USERNAME;\nSELECT GRANTEE, PRIVILEGE FROM DBA_SYS_PRIVS WHERE GRANTEE = '<USER>' ORDER BY PRIVILEGE;",
      [{"name": "USER", "desc": "用户名"}],
      "依据：YashanDB 与 Oracle 兼容性说明（Oracle 兼容 DBA 视图）与官方文档中心 " + YS_URL + "。DBA_USERS/DBA_SYS_PRIVS 列名（USERNAME/ACCOUNT_STATUS/DEFAULT_TABLESPACE/CREATED、GRANTEE/PRIVILEGE）为 Oracle 兼容命名，需在 YashanDB 23.2 实测核对。",
      "yashandb-014"),
]

KB_CATS = [
    ("日常巡检", "实例", ["kingbase-001", "kingbase-002"]),
    ("性能优化", "参数与缓存", ["kingbase-003", "kingbase-004"]),
    ("慢SQL", "定位", ["kingbase-005", "kingbase-006"]),
    ("锁 / 会话", "锁", ["kingbase-007", "kingbase-008"]),
    ("空间", "空间", ["kingbase-009", "kingbase-010"]),
    ("备份恢复", "备份", ["kingbase-011", "kingbase-012"]),
    ("高可用", "流复制", ["kingbase-013"]),
    ("用户 / 安全", "账号", ["kingbase-014"]),
]
YS_CATS = [
    ("日常巡检", "实例", ["yashandb-001", "yashandb-002"]),
    ("性能优化", "性能", ["yashandb-003", "yashandb-004"]),
    ("慢SQL", "定位", ["yashandb-005", "yashandb-006"]),
    ("锁 / 会话", "锁", ["yashandb-007", "yashandb-008"]),
    ("空间", "空间", ["yashandb-009", "yashandb-010"]),
    ("备份恢复", "备份", ["yashandb-011", "yashandb-012"]),
    ("高可用", "主备", ["yashandb-013"]),
    ("用户 / 安全", "账号", ["yashandb-014"]),
]

KB_DIRS = {"日常巡检": "日常巡检", "性能优化": "性能优化", "慢SQL": "慢SQL",
           "锁 / 会话": "锁-会话", "空间": "空间", "备份恢复": "备份恢复",
           "高可用": "高可用", "用户 / 安全": "用户-安全"}
KB_SLUGS = {
    "kingbase-001": "01-instance-version", "kingbase-002": "02-invalid-objects",
    "kingbase-003": "03-buffer-cache-hit-ratio", "kingbase-004": "04-gather-table-stats",
    "kingbase-005": "05-slow-sql-top", "kingbase-006": "06-explain-analyze",
    "kingbase-007": "07-blocking-locks", "kingbase-008": "08-kill-session",
    "kingbase-009": "09-tablespace-size", "kingbase-010": "10-large-tables-top",
    "kingbase-011": "11-sys-rman-backup", "kingbase-012": "12-pitr-drill",
    "kingbase-013": "13-replication-status", "kingbase-014": "14-users-roles",
}
YS_SLUGS = {
    "yashandb-001": "01-instance-version", "yashandb-002": "02-invalid-objects",
    "yashandb-003": "03-buffer-cache-hit-ratio", "yashandb-004": "04-gather-table-stats",
    "yashandb-005": "05-slow-sql-top", "yashandb-006": "06-explain-plan",
    "yashandb-007": "07-blocking-locks", "yashandb-008": "08-kill-session",
    "yashandb-009": "09-tablespace-usage", "yashandb-010": "10-large-tables-top",
    "yashandb-011": "11-backup-archive-status", "yashandb-012": "12-pitr-drill",
    "yashandb-013": "13-standby-status", "yashandb-014": "14-users-privileges",
}

def build(items, cats, db_id, name, versions, note, dirs, slugs, script_root):
    by_id = {it["id"]: it for it in items}
    categories = []
    for cat_name, sub_name, ids in cats:
        categories.append({"name": cat_name, "subcategories": [
            {"name": sub_name, "items": [by_id[i] for i in ids]}]})
    doc = {"id": db_id, "name": name, "versions": versions, "note": note,
           "categories": categories}
    with open(os.path.join(BASE, "data", f"toolbox-{db_id}.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    # sql files: sql field verbatim
    for cat_name, sub_name, ids in cats:
        d = os.path.join(BASE, "scripts", script_root, dirs[cat_name])
        os.makedirs(d, exist_ok=True)
        for i in ids:
            with open(os.path.join(d, slugs[i] + ".sql"), "w", encoding="utf-8") as f:
                f.write(by_id[i]["sql"] + "\n")

build(kb, KB_CATS, "kingbase", "金仓 KingBaseES", "KES V9 / V8.6",
      "国产化迁移方向，PG 兼容", KB_DIRS, KB_SLUGS, "kingbase")
build(ys, YS_CATS, "yashandb", "崖山 YashanDB", "YashanDB 23.2",
      "国产化迁移方向，Oracle 兼容", KB_DIRS, YS_SLUGS, "yashandb")
print("written")
