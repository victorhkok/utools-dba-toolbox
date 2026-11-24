#!/usr/bin/env python3
"""Generate openGauss toolbox data (14 items) + per-item .sql files.

Sources (official docs, docs.opengauss.org, 6.0.0 unless noted):
- System Views: https://docs.opengauss.org/en/docs/6.0.0/docs/DatabaseReference/system-views.html
- GS_WLM_SESSION_INFO / GS_WLM_SESSION_QUERY_INFO_ALL (duration/query/start_time/finish_time/status):
  https://docs.opengauss.org/en/docs/6.0.0/docs/DatabaseReference/gs_wlm_session_info.html
- Routine Maintenance (gs_check, pg_locks, pg_stat_activity, gs_dump, pg_database_size, VACUUM, EXPLAIN):
  https://docs.opengauss.org/en/docs/2.1.0/docs/Administratorguide/routine-maintenance.html
- Forcibly Terminating a Session (pg_terminate_backend):
  https://docs.opengauss.org/en/docs/2.1.0/docs/Developerguide/forcibly-terminating-a-session.html
- Analyzing the Status of a Query Statement (pg_stat_activity waiting=true):
  https://docs.opengauss.org/en/docs/3.1.0-lite/docs/Developerguide/analyzing-the-status-of-a-query-statement.html
- PG_STAT_REPLICATION (state/sync_state/sender_sent_location/receiver_replay_location):
  https://docs.opengauss.org/en/docs/3.1.1-lite/docs/Developerguide/pg_stat_replication.html
- gs_om: https://docs.opengauss.org/en/docs/1.0.0/docs/Toolreference/gs_om.html
- gs_probackup: https://docs.opengauss.org/en/docs/latest/tool_and_commandreference/gs_probackup.html
- Backup/restoration overview (gs_dump / gs_dumpall / gs_backup / gs_basebackup):
  https://docs.opengauss.org/en/docs/latest/database_om_guide/overview_for_backup_and_restoration.html
- GS_SLOW_QUERY_INFO discarded in 5.0.0 (use GS_WLM_SESSION_INFO instead):
  https://docs.opengauss.org/en/docs/5.0.0/docs/SQLReference/gs_slow_query_info-discarded.html
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DB = "opengauss"

# (category, subcategory, dir, slug, title, versions, risk, desc, sql, params, notes)
ITEMS = [
    ("日常巡检", "实例", "日常巡检", "version-cluster-status",
     "版本 / 集群状态（gs_om）", "5.0 / 6.0 LTS", "只读", "SELECT version() / gs_om -t status",
     "SELECT version();\n-- shell: gs_om -t status\n-- shell: gs_om -t status --detail",
     [],
     "依据：openGauss 官方手册 Routine Maintenance / gs_om。gs_om 须以 OS 用户 omm 执行；cluster_state 为 Normal 表示集群正常。"),
    ("日常巡检", "实例", "日常巡检", "database-size-connections",
     "库大小与当前连接数", "5.0 / 6.0 LTS", "只读", "pg_database_size / pg_stat_activity",
     "SELECT datname, pg_size_pretty(pg_database_size(datname)) AS size,\n  (SELECT count(*) FROM pg_stat_activity a WHERE a.datid = d.oid) AS connections\nFROM pg_database d ORDER BY pg_database_size(datname) DESC;",
     [],
     "依据：官方手册 Routine Maintenance（pg_database_size / SELECT count(*) FROM pg_stat_activity）。pg_stat_activity 沿用开源 PG 的视图名与列名；openGauss 中 pid 为线程 ID，且普通用户只能看到自己的会话状态。"),
    ("性能优化", "性能", "性能优化", "table-index-size-top",
     "大表 / 大索引 Top", "5.0 / 6.0 LTS", "只读", "pg_total_relation_size",
     "SELECT schemaname, relname, pg_size_pretty(pg_total_relation_size(relid)) AS total_size,\n  pg_size_pretty(pg_table_size(relid)) AS table_size,\n  pg_size_pretty(pg_indexes_size(relid)) AS indexes_size\nFROM pg_catalog.pg_statio_user_tables\nORDER BY pg_total_relation_size(relid) DESC LIMIT 20;",
     [],
     "依据：pg_total_relation_size / pg_table_size / pg_indexes_size 为 openGauss 沿用开源 PG 的函数，需在 openGauss 6.0 实测核对 pg_statio_user_tables 的列名。"),
    ("性能优化", "性能", "性能优化", "analyze-table-stats",
     "统计信息收集（ANALYZE）", "5.0 / 6.0 LTS", "谨慎", "ANALYZE",
     "-- 1. 先确认统计信息是否过期（只读）：\nSELECT schemaname, relname, last_analyze, last_autoanalyze, n_mod_since_analyze\nFROM pg_stat_user_tables WHERE schemaname = '<SCHEMA>' AND relname = '<TABLE>';\n-- 2. 确认后再执行（建议非高峰）：\n-- DANGER: ANALYZE <SCHEMA>.<TABLE>;",
     [{"name": "SCHEMA", "desc": "模式名"}, {"name": "TABLE", "desc": "表名"}],
     "依据：ANALYZE 与 pg_stat_user_tables 沿用开源 PG 语法；官方手册 Routine Maintenance 建议用 VACUUM 回收空间并更新统计信息。n_mod_since_analyze 列名需在 openGauss 6.0 实测核对。"),
    ("慢SQL", "定位", "慢SQL", "slow-sql-top-wlm",
     "慢SQL Top（GS_WLM_SESSION_INFO）", "5.0 / 6.0 LTS", "只读", "GS_WLM_SESSION_INFO",
     "SELECT dbname, username, duration AS duration_ms, start_time, finish_time, status,\n  left(query, 200) AS query_snippet\nFROM gs_wlm_session_info\nWHERE duration > <THRESHOLD_MS>\nORDER BY duration DESC LIMIT 20;",
     [{"name": "THRESHOLD_MS", "desc": "慢查询阈值（毫秒），如 1000"}],
     "依据：官方手册 GS_WLM_SESSION_INFO 列名 duration（毫秒）、dbname、username、start_time、finish_time、status、query 均已核对。注意：该视图仅 sysadmin 可查，且仅在 postgres 库可查；GS_SLOW_QUERY_INFO 在 5.0 已废弃，不要用；enable_resource_record 须为 on 才会定期入库，需在 6.0 实测核对。"),
    ("慢SQL", "定位", "慢SQL", "explain-plan",
     "执行计划（EXPLAIN）", "5.0 / 6.0 LTS", "只读", "EXPLAIN",
     "EXPLAIN SELECT * FROM <SCHEMA>.<TABLE> WHERE <CONDITION>;",
     [{"name": "SCHEMA.TABLE", "desc": "表名"}, {"name": "CONDITION", "desc": "WHERE 条件"}],
     "依据：官方手册 Routine Maintenance 建议用 EXPLAIN 查看执行计划。只给不执行的 EXPLAIN；EXPLAIN ANALYZE 会真实执行，勿对写操作使用，需在 openGauss 6.0 实测核对。"),
    ("锁/会话", "锁", "锁-会话", "blocking-locks",
     "阻塞锁 / 等待会话", "5.0 / 6.0 LTS", "只读", "pg_locks / pg_stat_activity",
     "-- 正在等待锁的会话（官方手册示例：pg_stat_activity WHERE waiting = true）：\nSELECT datname, usename, pid, state, waiting, now() - query_start AS wait_duration, left(query, 200) AS query\nFROM pg_stat_activity WHERE waiting = true ORDER BY query_start;\n-- 锁持有情况：\nSELECT locktype, mode, granted, count(*) AS cnt FROM pg_locks GROUP BY locktype, mode, granted ORDER BY cnt DESC;",
     [],
     "依据：官方手册 Analyzing the Status of a Query Statement（waiting = true）与 Routine Maintenance（SELECT * FROM pg_locks）。pg_locks / pg_stat_activity 沿用开源 PG；openGauss 的 waiting 列与 PG 行为一致，需在 6.0 实测核对。"),
    ("锁/会话", "锁", "锁-会话", "kill-session",
     "强制终止会话", "5.0 / 6.0 LTS", "危险", "pg_terminate_backend",
     "-- 1. 先确认（只读查询）：\nSELECT datid, pid, usename, state, left(query, 200) AS query FROM pg_stat_activity WHERE pid = <PID>;\n-- 2. 确认无误后再执行（危险）：\n-- DANGER: SELECT pg_terminate_backend(<PID>);",
     [{"name": "PID", "desc": "会话线程 ID（pg_stat_activity.pid）"}],
     "依据：官方手册 Forcibly Terminating a Session（SELECT pg_terminate_backend(<pid>)）。openGauss 的 pid 是线程 ID（bigint），不是 OS 进程号；杀会话前务必确认业务影响。"),
    ("空间/存储", "空间", "空间", "tablespace-usage",
     "表空间使用情况", "5.0 / 6.0 LTS", "只读", "pg_tablespace_size",
     "SELECT spcname, pg_size_pretty(pg_tablespace_size(spcname)) AS size,\n  pg_tablespace_location(oid) AS location\nFROM pg_tablespace ORDER BY pg_tablespace_size(spcname) DESC;",
     [],
     "依据：pg_tablespace_size / pg_tablespace 沿用开源 PG。pg_tablespace_location 列名与返回值需在 openGauss 6.0 实测核对。"),
    ("空间/存储", "空间", "空间", "dead-tuples-top",
     "死元组 / 膨胀检查", "5.0 / 6.0 LTS", "只读", "pg_stat_user_tables",
     "SELECT schemaname, relname, n_live_tup, n_dead_tup,\n  round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,\n  last_vacuum, last_autovacuum, last_analyze\nFROM pg_stat_user_tables\nWHERE n_dead_tup > 0 ORDER BY n_dead_tup DESC LIMIT 20;",
     [],
     "依据：pg_stat_user_tables 沿用开源 PG；官方手册 Routine Maintenance 建议用 VACUUM 回收空间。死元组占比高时先在测试环境验证 VACUUM 影响，列名需在 openGauss 6.0 实测核对。"),
    ("备份恢复", "备份", "备份恢复", "gs-dump-logical-backup",
     "逻辑备份（gs_dump）", "5.0 / 6.0 LTS", "谨慎", "gs_dump",
     "-- shell: gs_dump <DBNAME> -p <PORT> -f <OUTFILE>.sql -U <USER>\n-- shell: gs_dump <DBNAME> -p <PORT> -n <SCHEMA> -f <OUTFILE>.sql\n-- shell: gs_dump <DBNAME> -p <PORT> -t <TABLE> -f <OUTFILE>.sql\n-- shell: gs_dumpall -p <PORT> -f <OUTFILE>.sql\n-- 恢复（文本格式用 gsql，归档格式用 gs_restore）：\n-- shell: gsql -d <DBNAME> -p <PORT> -f <OUTFILE>.sql",
     [{"name": "DBNAME", "desc": "数据库名"}, {"name": "PORT", "desc": "端口（默认 26000）"}, {"name": "OUTFILE", "desc": "备份输出文件"}],
     "依据：官方手册 Routine Maintenance 与备份恢复总览（gs_dump / gs_dumpall / gs_restore）。文本格式恢复慢、大库慎用；备份前确认磁盘余量。"),
    ("备份恢复", "备份", "备份恢复", "gs-probackup-physical",
     "物理备份与恢复（gs_probackup）", "5.0 / 6.0 LTS", "危险", "gs_probackup",
     "-- 1. 先查看已有备份（只读）：\n-- shell: gs_probackup show -B <BACKUP_PATH> --instance=<INSTANCE>\n-- 2. 全量备份（需先 init / add-instance，见手册）：\n-- shell: gs_probackup backup -B <BACKUP_PATH> --instance=<INSTANCE> -b FULL\n-- 3. 恢复为危险操作，先在测试库演练：\n-- DANGER: gs_probackup restore -B <BACKUP_PATH> --instance=<INSTANCE>;",
     [{"name": "BACKUP_PATH", "desc": "备份目录"}, {"name": "INSTANCE", "desc": "备份实例名"}],
     "依据：官方手册 gs_probackup（支持全量/增量/定期/远程备份、PTRACK 增量需 enable_cbm_tracking=on）。init 与 add-instance 的完整参数需按手册核对；恢复前务必先停写并做副本，需在 6.0 实测核对。"),
    ("高可用/容灾", "主备", "高可用", "replication-lag",
     "主备复制状态与延迟", "5.0 / 6.0 LTS", "只读", "pg_stat_replication / gs_om",
     "-- 主库视角：备库同步状态与日志位置（官方手册列名已核对）：\nSELECT application_name, client_addr, state, sync_state, sync_priority,\n  sender_sent_location, receiver_write_location, receiver_flush_location, receiver_replay_location\nFROM pg_stat_replication;\n-- shell: gs_om -t status",
     [],
     "依据：官方手册 PG_STAT_REPLICATION（state / sync_state / sender_sent_location / receiver_replay_location）与 gs_om。openGauss 沿用 PG 的 pg_stat_replication 视图名，但 state 取值（catchup/streaming）与开源 PG 略有不同，需在 6.0 实测核对。"),
    ("用户/安全", "用户", "用户-安全", "users-and-privileges",
     "用户与权限", "5.0 / 6.0 LTS", "谨慎", "pg_roles / CREATE USER",
     "-- 1. 先查看现有用户与属性（只读）：\nSELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin, rolvaliduntil FROM pg_roles ORDER BY rolname;\n-- 2. 新建用户（模板，密码须符合 openGauss 复杂度要求）：\n-- DANGER: CREATE USER <USERNAME> WITH PASSWORD '<PASSWORD>';\n-- 3. 授权示例：\n-- DANGER: GRANT SELECT ON <SCHEMA>.<TABLE> TO <USERNAME>;",
     [{"name": "USERNAME", "desc": "用户名"}, {"name": "PASSWORD", "desc": "密码（符合复杂度要求）"}],
     "依据：pg_roles 沿用开源 PG。CREATE USER / GRANT 语法沿用 PG，但 openGauss 默认密码复杂度策略与 PG 不同，弱密码会被拒绝，密码规则需在 6.0 实测核对；切勿在脚本里留真实密码。"),
]

def build():
    cats = {}
    order = []
    for cat, sub, d, slug, title, vers, risk, desc, sql, params, notes in ITEMS:
        if cat not in cats:
            cats[cat] = {"name": cat, "subcategories": []}
            order.append(cat)
        subs = cats[cat]["subcategories"]
        s = next((x for x in subs if x["name"] == sub), None)
        if s is None:
            s = {"name": sub, "items": []}
            subs.append(s)
        s["items"].append({"title": title, "versions": vers, "risk": risk,
                           "desc": desc, "sql": sql, "params": params, "notes": notes})
    # assign ids in file order
    n = 0
    for cat in order:
        for sub in cats[cat]["subcategories"]:
            for it in sub["items"]:
                n += 1
                it["id"] = f"{DB}-{n:03d}"
    data = {"id": DB, "name": "openGauss", "versions": "5.0 / 6.0 LTS",
            "note": "华为开源，PostgreSQL 内核，PG 兼容视图与 openGauss 专属视图（GS_WLM_*）并存",
            "categories": [cats[c] for c in order]}
    os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
    with open(os.path.join(BASE, "data", f"toolbox-{DB}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    # .sql files, numbered per category dir (same convention as dameng/tidb)
    counters = {}
    idx = 0
    for cat, sub, d, slug, title, vers, risk, desc, sql, params, notes in ITEMS:
        idx += 1
        counters[d] = counters.get(d, 0) + 1
        outdir = os.path.join(BASE, "scripts", DB, d)
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, f"{counters[d]:02d}-{slug}.sql"), "w", encoding="utf-8") as f:
            f.write(sql + "\n")
    print(f"{DB}: {idx} items written")

if __name__ == "__main__":
    build()
