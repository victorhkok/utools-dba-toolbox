#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill MySQL 45 items: toolbox-mysql.json + scripts/mysql/<cat>/NN-slug.sql
Order MUST match toolbox.json MySQL order exactly. Titles/versions/risk untouched.
"""
import json, pathlib, re
ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "data" / "toolbox.json"
OUT = ROOT / "data" / "toolbox-mysql.json"
SCRIPTS = ROOT / "scripts" / "mysql"

CAT_DIR = {"日常巡检": "daily-check", "性能优化": "performance", "慢SQL": "slow-sql",
           "锁 / 会话": "lock-session", "空间 / 存储": "storage", "备份恢复": "backup-restore",
           "高可用 / 复制": "ha-replication", "用户 / 安全": "user-security"}

# Each entry: (slug, sql, params, notes) in toolbox.json order
E = [
# --- 日常巡检 / 实例与状态 (5) ---
("instance-version-uptime",
 "SELECT VERSION() AS version;\nSHOW GLOBAL STATUS LIKE 'Uptime';\nSHOW GLOBAL STATUS LIKE 'Threads_connected';",
 [], "Uptime 单位是秒；先看 VERSION 再对版本，其他条目的版本判断都以它为准。"),
("connections-max",
 "SHOW GLOBAL STATUS LIKE 'Threads_connected';\nSHOW GLOBAL STATUS LIKE 'Threads_running';\nSHOW VARIABLES LIKE 'max_connections';\nSELECT COUNT(*) AS processlist_count FROM information_schema.PROCESSLIST;",
 [], "Threads_connected 接近 max_connections 时先查 PROCESSLIST 找长连接，不要直接调大 max_connections。"),
("slow-query-settings",
 "SHOW VARIABLES LIKE 'slow_query_log';\nSHOW VARIABLES LIKE 'long_query_time';\nSHOW VARIABLES LIKE 'slow_query_log_file';\nSHOW VARIABLES LIKE 'log_queries_not_using_indexes';",
 [], "只读查看开关；改 long_query_time 建议先在测试库评估，生产改动用 SET GLOBAL 并记录。"),
("error-log-path",
 "SHOW VARIABLES LIKE 'log_error';",
 ["<log_error路径>"],
 "先用上面 SQL 拿到 log_error 路径，再在 shell 里 grep；SQL 本身不读日志文件。shell: grep -iE 'ERROR|Warning' \"<log_error路径>\" | tail -n 50"),
("events-status",
 "SHOW VARIABLES LIKE 'event_scheduler';\nSHOW EVENTS;\nSELECT EVENT_SCHEMA, EVENT_NAME, STATUS, LAST_EXECUTED FROM information_schema.EVENTS LIMIT 20;",
 [], "event_scheduler=OFF 时 EVENT 不执行；STATUS=SLAVESIDE_DISABLED 表示在从库上被禁用，是正常现象。"),
# --- 日常巡检 / 健康指标 (3) ---
("innodb-buffer-pool-hit-rate",
 "SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';\nSELECT ROUND(100 * (1 - SUM(CASE WHEN VARIABLE_NAME = 'Innodb_buffer_pool_reads' THEN VARIABLE_VALUE ELSE 0 END) / NULLIF(SUM(CASE WHEN VARIABLE_NAME = 'Innodb_buffer_pool_read_requests' THEN VARIABLE_VALUE ELSE 0 END), 0)), 2) AS buffer_pool_hit_pct FROM performance_schema.global_status WHERE VARIABLE_NAME IN ('Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests');",
 [], "命中率正常应 >99%；低于 99% 先看 Buffer Pool 是否太小，不要直接归咎于 SQL。"),
("qps-tps",
 "SHOW GLOBAL STATUS LIKE 'Questions';\nSHOW GLOBAL STATUS LIKE 'Com_commit';\nSHOW GLOBAL STATUS LIKE 'Com_rollback';\nSHOW GLOBAL STATUS LIKE 'Uptime';",
 [], "QPS=Questions/Uptime、TPS=(Com_commit+Com_rollback)/Uptime；单点值没意义，隔 10 秒取两次再算差值。"),
("tmp-table-sort-overflow",
 "SHOW GLOBAL STATUS LIKE 'Created_tmp%';\nSHOW GLOBAL STATUS LIKE 'Sort_merge_passes';\nSHOW GLOBAL STATUS LIKE 'Sort_scan';\nSHOW GLOBAL STATUS LIKE 'Sort_range';",
 [], "Created_tmp_disk_tables 持续增长说明内存临时表不够或 SQL 有大排序，先看 SQL 再调 tmp_table_size。"),
# --- 性能优化 / 参数与内存 (3) ---
("key-variables",
 "SHOW VARIABLES WHERE Variable_name IN ('innodb_buffer_pool_size', 'innodb_log_file_size', 'innodb_flush_log_at_trx_commit', 'max_connections', 'innodb_buffer_pool_instances', 'tmp_table_size', 'max_heap_table_size', 'sort_buffer_size', 'join_buffer_size', 'innodb_io_capacity', 'innodb_flush_method');",
 [], "只读速查；8.0 已移除 query_cache 相关变量，不在列表里，查不到是正常的。"),
("buffer-pool-recommendation",
 "SELECT @@innodb_buffer_pool_size / 1024 / 1024 / 1024 AS buffer_pool_gb;\nSHOW VARIABLES LIKE 'innodb_buffer_pool_instances';\nSHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_total';",
 [], "专用数据库服务器建议 Buffer Pool 占物理内存 70%-80%；先用 free -g 看整机内存，再算，不要只看当前值。"),
("histogram-column-statistics",
 "SELECT SCHEMA_NAME, TABLE_NAME, COLUMN_NAME, HISTOGRAM FROM information_schema.COLUMN_STATISTICS LIMIT 50;",
 [],
 "仅 8.0+：information_schema.COLUMN_STATISTICS，HISTOGRAM 是 JSON；5.7 没有这张表，查不到不是故障。新增直方图用 ANALYZE TABLE <库>.<表> UPDATE HISTOGRAM ON <列>。"),
# --- 性能优化 / 索引 (4) ---
("unused-indexes",
 "SELECT * FROM sys.schema_unused_indexes LIMIT 50;",
 [], "sys 库视图，5.7+ 可用；删索引前先确认该表在业务低峰的访问情况，误删恢复要重建。"),
("redundant-indexes",
 "SELECT * FROM sys.schema_redundant_indexes LIMIT 50;",
 [], "sys 库视图；冗余索引会拖慢写入，删之前先用不可见索引（8.0+）灰度验证。"),
("index-cardinality",
 "SHOW INDEX FROM <db>.<table>;\nSELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, COLUMN_NAME, CARDINALITY FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = '<db>' AND TABLE_NAME = '<table>' LIMIT 50;",
 ["<db>", "<table>"],
 "CARDINALITY 越接近表行数选择性越好；刚 ANALYZE 完的基数才准，过期统计会误导。"),
("invisible-index",
 "SELECT INDEX_NAME, IS_VISIBLE FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = '<db>' AND TABLE_NAME = '<table>' LIMIT 50;\n-- 设为不可见（仅 8.0+，灰度验证用）：\n-- ALTER TABLE <db>.<table> ALTER INDEX <index> INVISIBLE;\n-- 恢复可见：ALTER TABLE <db>.<table> ALTER INDEX <index> VISIBLE;",
 ["<db>", "<table>", "<index>"],
 "仅 8.0+：IS_VISIBLE 列和 ALTER INDEX ... INVISIBLE/VISIBLE 都是 8.0 才有；先 INVISIBLE 观察一周无问题再 DROP。"),
# --- 慢SQL / 定位 (4) ---
("slow-log-analysis",
 "-- shell: mysqldumpslow -s t -t 20 \"<slow_log路径>\"\n-- shell: pt-query-digest --type slowlog \"<slow_log路径>\" | head -n 100\nSHOW VARIABLES LIKE 'slow_query_log_file';",
 ["<slow_log路径>"],
 "先用上面 SQL 拿到慢日志路径再分析；pt-query-digest 需单独安装 percona-toolkit，不在 MySQL 自带。"),
("performance-schema-top-sql",
 "-- 需 performance_schema 开启（默认开），否则结果为空。\nSELECT DIGEST_TEXT, COUNT_STAR, ROUND(SUM_TIMER_WAIT / 1000000000000, 2) AS sum_sec, ROUND(AVG_TIMER_WAIT / 1000000000000, 4) AS avg_sec, SUM_ROWS_EXAMINED, SUM_ROWS_SENT FROM performance_schema.events_statements_summary_by_digest ORDER BY SUM_TIMER_WAIT DESC LIMIT 20;",
 [], "需 performance_schema 开启；SUM_TIMER_WAIT 单位是皮秒，已换算成秒；DIGEST_TEXT 是归一化后的 SQL。"),
("statements-95th-percentile",
 "SELECT * FROM sys.statements_with_runtimes_in_95th LIMIT 20;",
 [], "sys 库视图，5.7+ 可用；看 95 分位耗时而不是平均耗时，平均值会被少数慢查询拉高或拉低。"),
("full-table-scan-sql",
 "SELECT DIGEST_TEXT, COUNT_STAR, SUM_NO_INDEX_USED, SUM_NO_GOOD_INDEX_USED FROM performance_schema.events_statements_summary_by_digest WHERE SUM_NO_INDEX_USED > 0 ORDER BY SUM_NO_INDEX_USED DESC LIMIT 20;\nSELECT * FROM sys.statements_with_full_table_scans LIMIT 20;",
 [], "需 performance_schema 开启；SUM_NO_INDEX_USED>0 不等于一定是坏 SQL，小表全表扫描可能是合理的。"),
# --- 慢SQL / 执行计划 (3) ---
("explain-analyze",
 "-- 8.0.18+ 才有 EXPLAIN ANALYZE；5.7/8.0.17 及以下只能用 EXPLAIN。\n-- EXPLAIN ANALYZE 会真实执行 SQL，只对 SELECT 用，不要对 UPDATE/DELETE 用。\nEXPLAIN <SELECT 语句>;\n-- EXPLAIN ANALYZE <SELECT 语句>;",
 ["<SELECT 语句>"],
 "仅 8.0.18+ 才有 EXPLAIN ANALYZE；它会真实执行，只对 SELECT 用，生产上先在从库或测试库跑。"),
("explain-index-vs-full-scan",
 "EXPLAIN <SELECT 语句>;",
 ["<SELECT 语句>"],
 "看 type 列：ALL=全表扫描要警惕，ref/range/const 一般较好；再看 Extra 是否有 Using filesort / Using temporary。"),
("explain-join-order",
 "EXPLAIN <SELECT 语句>;",
 ["<SELECT 语句>"],
 "看 id 顺序和 rows：rows 小的表先驱动一般更优；JOIN 字段两边类型不一致会导致索引失效。"),
# --- 锁 / 会话 / 锁 (4) ---
("innodb-lock-waits",
 "SELECT * FROM sys.innodb_lock_waits LIMIT 20;",
 [], "sys 库视图，5.7+ 可用；先看 blocking_pid 再决定杀谁，杀等待方通常没用，要杀阻塞方。"),
("deadlock-log",
 "SHOW ENGINE INNODB STATUS;",
 [], "输出里找 LATEST DETECTED DEADLOCK 一节；只读查看，死锁本身由 InnoDB 自动回滚其中一个事务。"),
("kill-connection",
 "-- 先查，再杀：\nSELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO FROM information_schema.PROCESSLIST WHERE TIME > 300 ORDER BY TIME DESC LIMIT 20;\n-- DANGER: 先确认该连接的业务影响，再执行下面一行，<connection_id> 填上面查到的 ID：\n-- KILL CONNECTION <connection_id>;",
 ["<connection_id>"],
 "DANGER：KILL 前先确认 ID 对应的 SQL 和业务影响；KILL CONNECTION 只断连接，KILL QUERY 只停当前查询，默认 KILL 等于 KILL CONNECTION。"),
("long-transactions",
 "SELECT trx_id, trx_state, trx_started, trx_mysql_thread_id, trx_query FROM information_schema.INNODB_TRX WHERE trx_started < NOW() - INTERVAL 30 MINUTE LIMIT 20;",
 [], "长事务会拖住 undo 和锁；先看 trx_query 再决定是等它提交还是联系业务方，不要直接 KILL。"),
# --- 空间 / 存储 / 空间 (4) ---
("db-table-size-top20",
 "SELECT TABLE_SCHEMA, TABLE_NAME, ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb, ROUND(SUM(DATA_LENGTH) / 1024 / 1024, 2) AS data_mb, ROUND(SUM(INDEX_LENGTH) / 1024 / 1024, 2) AS index_mb, SUM(TABLE_ROWS) AS rows_est FROM information_schema.TABLES GROUP BY TABLE_SCHEMA, TABLE_NAME ORDER BY size_mb DESC LIMIT 20;",
 [], "TABLE_ROWS 是估算值（InnoDB），不要当精确行数；大小按 DATA_LENGTH+INDEX_LENGTH 算。"),
("fragmentation-optimize",
 "SELECT TABLE_SCHEMA, TABLE_NAME, ROUND(DATA_FREE / 1024 / 1024, 2) AS data_free_mb, ROUND(DATA_FREE / NULLIF(DATA_LENGTH + INDEX_LENGTH, 0) * 100, 2) AS free_pct FROM information_schema.TABLES WHERE DATA_FREE > 0 ORDER BY DATA_FREE DESC LIMIT 20;\n-- 评估后、非高峰再执行：OPTIMIZE TABLE <db>.<table>;",
 ["<db>", "<table>"],
 "谨慎：OPTIMIZE TABLE 会重建表，8.0 InnoDB 虽然在线但仍占 IO 和磁盘空间，先确认剩余磁盘大于表大小。"),
("ibdata-undo-redo-size",
 "SHOW VARIABLES LIKE 'innodb_data_file_path';\nSHOW VARIABLES LIKE 'innodb_data_home_dir';\nSHOW VARIABLES LIKE 'innodb_undo_directory';\nSHOW VARIABLES LIKE 'innodb_log_file_size';\nSHOW VARIABLES LIKE 'innodb_log_files_in_group';\nSHOW VARIABLES LIKE 'innodb_log_group_home_dir';",
 [], "只读查看路径和大小；ibdata1 只增不减是正常现象，不要直接删文件，删了实例起不来。"),
("disk-usage-warning",
 "SELECT TABLE_SCHEMA, ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 / 1024, 2) AS total_gb FROM information_schema.TABLES GROUP BY TABLE_SCHEMA ORDER BY total_gb DESC LIMIT 20;",
 [],
 "SQL 只算库大小，磁盘余量要另看 shell：df -h <datadir>；datadir 路径用 SHOW VARIABLES LIKE 'datadir' 查。"),
# --- 备份恢复 / 逻辑备份 (3) ---
("mysqldump-backup",
 "-- shell: 全库备份\n-- mysqldump --single-transaction --quick --master-data=2 --routines --events --triggers -u <user> -p <db> > \"<backup_dir>/<db>_$(date +%F).sql\"\n-- shell: 单表备份\n-- mysqldump --single-transaction --quick -u <user> -p <db> <table> > \"<backup_dir>/<db>_<table>.sql\"\n-- 备份前先确认 binlog 位置：\nSHOW BINARY LOGS;",
 ["<user>", "<db>", "<table>", "<backup_dir>"],
 "谨慎：--single-transaction 只对 InnoDB 一致；MyISAM 表不在此保证内；8.4 里 --master-data 已改名 --source-data=2，8.0 及以下用 --master-data=2；-p 后不要在命令行写明文密码，会进 shell 历史。"),
("mydumper-backup",
 "-- shell: mydumper -u <user> -B <db> -o \"<backup_dir>\" -t 4 --routines --events --triggers --compress\n-- shell: 恢复用 myloader -u <user> -d \"<backup_dir>\" -t 4\n-- 备份前先确认：\nSHOW BINARY LOGS;",
 ["<user>", "<db>", "<backup_dir>"],
 "谨慎：mydumper 需单独安装，不在 MySQL 自带；大库首选并行备份，恢复前先在测试库演练一遍。"),
("binlog-pitr",
 "-- DANGER: 时间点恢复会回放 binlog，先在测试库演练，确认起止时间后再在目标库执行。\n-- shell: mysqlbinlog --start-datetime=\"2026-11-24 10:00:00\" --stop-datetime=\"2026-11-24 11:00:00\" \"<binlog文件>\" | mysql -u <user> -p\n-- 先确认 binlog 列表：\nSHOW BINARY LOGS;",
 ["<binlog文件>", "<user>"],
 "DANGER：PITR 是回放写操作，起止时间错了会多回放或少回放；先 SHOW BINARY LOGS 确认文件名，再在测试库跑一遍。"),
# --- 备份恢复 / 物理备份 (3) ---
("xtrabackup-full-incremental",
 "-- shell: 全备\n-- xtrabackup --backup --target-dir=\"<base_dir>\" -u <user> -p\n-- shell: 增量（基于全备目录）\n-- xtrabackup --backup --target-dir=\"<inc_dir>\" --incremental-basedir=\"<base_dir>\" -u <user> -p\n-- 备份后检查：\nSHOW BINARY LOGS;",
 ["<user>", "<base_dir>", "<inc_dir>"],
 "谨慎：XtraBackup 需单独安装，版本要和 MySQL 大版本对应；增量备份依赖全备目录，不要删全备。"),
("xtrabackup-restore-drill",
 "-- DANGER: 恢复演练只在测试库做，--copy-back 会覆盖 datadir，执行前必须先停 MySQL。\n-- shell: xtrabackup --prepare --apply-log-only --target-dir=\"<base_dir>\"\n-- shell: xtrabackup --prepare --target-dir=\"<base_dir>\"\n-- shell: xtrabackup --copy-back --target-dir=\"<base_dir>\" --datadir=\"<datadir>\"",
 ["<base_dir>", "<datadir>"],
 "DANGER：只在测试库演练；--copy-back 前必须停库并确认 datadir 为空或已备份，生产库不要直接跑。"),
("binlog2sql-flashback",
 "-- shell: python binlog2sql.py -h<host> -u<user> -d<db> -t<table> --start-file=\"<binlog文件>\" --start-datetime=\"2026-11-24 10:00:00\" --stop-datetime=\"2026-11-24 11:00:00\" -B\n-- 闪回只对 DML 有效，先确认：\nSHOW VARIABLES LIKE 'binlog_format';",
 ["<host>", "<user>", "<db>", "<table>", "<binlog文件>"],
 "DANGER：binlog2sql 需单独安装，只支持 ROW 格式 binlog 的 DML 闪回；生成的反向 SQL 先人工检查再执行，不要直接管道进 mysql。"),
# --- 高可用 / 复制 / 主从 (3) ---
("replication-delay",
 "-- 5.7: SHOW SLAVE STATUS\n-- 8.0+: SHOW REPLICA STATUS（5.7 的 SHOW SLAVE STATUS 在 8.0 仍可用，8.4 已移除）\nSHOW SLAVE STATUS;",
 [],
 "看 Seconds_Behind_Master（8.0 从库状态里叫 Seconds_Behind_Source）；延迟先看 SQL 线程是否在跑，再看大事务。"),
("replication-error",
 "SHOW SLAVE STATUS;\nSELECT SERVICE_STATE, LAST_ERROR_NUMBER, LAST_ERROR_MESSAGE FROM performance_schema.replication_applier_status LIMIT 20;",
 [], "先看 SHOW 里的 Last_IO_Error / Last_SQL_Error，再看 performance_schema 的 applier 状态；不要直接跳过错误（sql_slave_skip_counter）。"),
("gtid-consistency",
 "SHOW VARIABLES LIKE 'gtid_mode';\nSHOW VARIABLES LIKE 'enforce_gtid_consistency';\nSELECT @@GLOBAL.gtid_executed AS gtid_executed;\nSELECT @@GLOBAL.gtid_purged AS gtid_purged;",
 [], "主从的 Retrieved_Gtid_Set 和 Executed_Gtid_Set 对不上先别切主，先查哪段 GTID 缺了；gtid_purged 被清掉的 GTID 找不回来。"),
# --- 高可用 / 复制 / MGR / MHA (3) ---
("mgr-members",
 "SELECT MEMBER_ID, MEMBER_HOST, MEMBER_PORT, MEMBER_STATE, MEMBER_ROLE FROM performance_schema.replication_group_members;",
 [],
 "仅 8.0+：replication_group_members 是 MGR 的表，5.7 没有；MEMBER_STATE=ONLINE 且只有一个 PRIMARY 才是正常。"),
("mgr-set-primary",
 "-- 先查当前主节点 UUID：\nSELECT MEMBER_ID, MEMBER_HOST, MEMBER_ROLE FROM performance_schema.replication_group_members;\n-- DANGER: 切换主节点，先确认业务影响和新主已同步：\n-- SELECT group_replication_set_as_primary('<primary_uuid>');",
 ["<primary_uuid>"],
 "DANGER：仅 8.0+；group_replication_set_as_primary 是函数调用形式（SELECT ...），切换前确认新主已追上，否则会丢数据。"),
("mha-failover-drill",
 "-- shell: 检查 SSH 和复制\n-- masterha_check_ssh --conf=\"<mha_conf>\"\n-- masterha_check_repl --conf=\"<mha_conf>\"\n-- shell: 演练切换（只在演练环境，interactive=0 表示不交互确认，务必先确认）\n-- masterha_master_switch --conf=\"<mha_conf>\" --master_state=alive --new_master_host=\"<new_master_host>\" --orig_master_is_new_slave --running_updates_limit=100 --interactive=0\n-- 切换前先确认主从：\nSHOW SLAVE STATUS;",
 ["<mha_conf>", "<new_master_host>"],
 "谨慎：MHA 需单独安装；masterha_master_switch 是真实切换，只在演练环境跑，生产切换要走审批和停写窗口。"),
# --- 用户 / 安全 / 账号 (3) ---
("users-privileges",
 "SELECT User, Host FROM mysql.user LIMIT 50;\n-- 查某账号权限：SHOW GRANTS FOR '<user>'@'<host>';",
 ["<user>", "<host>"],
 "先看 mysql.user 全量账号，再对单个账号 SHOW GRANTS；不要直接 SELECT * FROM mysql.user，含敏感列。"),
("weak-no-password-accounts",
 "SELECT User, Host, plugin FROM mysql.user WHERE authentication_string = '' OR authentication_string IS NULL LIMIT 50;",
 [], "authentication_string 为空的账号可能是无密码或用 socket 认证；plugin=auth_socket 的本地账号是正常情况，不要误杀。"),
("audit-log",
 "SHOW VARIABLES LIKE 'audit_log%';\nSELECT PLUGIN_NAME, PLUGIN_STATUS FROM information_schema.PLUGINS WHERE PLUGIN_NAME = 'audit_log';",
 [],
 "5.7 需 INSTALL PLUGIN audit_log SONAME 'audit_log.so'，8.0 用 audit_log_filter；两个版本的审计配置不同，先按版本确认再开。"),
]

def slugify(s):
    return s

def main():
    src = json.loads(SRC.read_text(encoding="utf-8"))
    mysql = next(d for d in src["databases"] if d["id"] == "mysql")
    # flatten in order
    flat = []
    for cat in mysql["categories"]:
        for sub in cat["subcategories"]:
            for item in sub["items"]:
                flat.append((cat["name"], sub["name"], item))
    assert len(flat) == 45, f"flat={len(flat)}"
    assert len(E) == 45, f"E={len(E)}"
    # enrich copy
    import copy
    out = copy.deepcopy(mysql)
    counters = {}
    files = []
    idx = 0
    for cat in out["categories"]:
        for sub in cat["subcategories"]:
            for item in sub["items"]:
                cat_name, sub_name, _orig = flat[idx]
                assert cat["name"] == cat_name and sub["name"] == sub_name, (cat, sub)
                slug, sql, params, notes = E[idx]
                item["sql"] = sql
                item["params"] = params
                item["notes"] = notes
                # file
                key = (CAT_DIR[cat_name], sub_name)
                counters[key] = counters.get(key, 0) + 1
                nn = f"{counters[key]:02d}"
                d = SCRIPTS / CAT_DIR[cat_name]
                d.mkdir(parents=True, exist_ok=True)
                fname = f"{nn}-{slug}.sql"
                fpath = d / fname
                header = (f"-- {item['title']}\n-- 适用版本：{item['versions']}\n-- 风险：{item['risk']}\n"
                          f"-- 说明：{item['desc']}\n-- 大类：{cat_name} / 小类：{sub_name}\n")
                # shell-command items: sql already starts with -- shell:, keep as-is after header
                body = sql if sql.endswith("\n") else sql + "\n"
                fpath.write_text(header + body, encoding="utf-8")
                files.append(str(fpath.relative_to(ROOT)))
                idx += 1
    out_data = {"id": mysql["id"], "name": mysql["name"], "versions": mysql["versions"],
                "note": mysql["note"], "categories": out["categories"]}
    OUT.write_text(json.dumps(out_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"items={idx} files={len(files)}")
    for f in files:
        print(f)

if __name__ == "__main__":
    main()
