# -*- coding: utf-8 -*-
"""为 uTools DBA 工具箱新增 TDSQL 与 GoldenDB 两个库的脚本（各 14 条，共 28 条）。

依据：
- TDSQL：腾讯云官方文档《TDSQL for MySQL Overview》
  https://www.tencentcloud.com/document/product/1042/33311
  （分布式、Shared Nothing、自动分片 shardkey、主从 HA、备份/恢复/容灾/监控/迁移）
  《Backup Mode》https://intl.cloud.tencent.com/document/product/1042/36423
  （全量 + 基于 binlog 的增量备份，保留期默认 7 天，1-365 天）
  《TDSQL PostgreSQL版 操作指南》（腾讯云官方 PDF）
  https://main.qcloudimg.com/raw/document/product/pdf/1129_39781_cn.pdf
  （分布式/集中式、CN/DN/GTM、不提供 super user、备份默认 7 天、只支持整实例回档生成新实例）
  TDSQL MySQL 版高度兼容 MySQL 语法（官方概述），故 MySQL 版条目使用
  information_schema / performance_schema 等 MySQL 标准字典视图。
- GoldenDB：中兴通讯《GoldenDB 数据库 V6 技术白皮书》（2025-08-15 发布）
  https://www.zte.com.cn/content/dam/zte-site/res-www-zte-com-cn/goldendb/260709/%E4%B8%AD%E5%85%B4%E9%80%9A%E8%AE%AFGoldenDB%E6%95%B0%E6%8D%AE%E5%BA%93V6%E6%8A%80%E6%9C%AF%E7%99%BD%E7%9A%AE%E4%B9%A6_20260708.pdf
  （分布式/集中式/混合部署；CN 计算节点 + DN 数据节点 + GTM + 管理节点；
  分片组 DBGroup 一主多备强同步；Range/Hash/List 分片、DUPLICATE 复制表；
  两阶段提交分布式事务；逻辑/物理备份 + 按时间点恢复；Insight/OMM 运维）
  GoldenDB 未找到公开的 SQL 手册（zte.com.cn 站内无结果），DN 基于 MySQL 内核、
  高度兼容 MySQL 语法与协议（白皮书及官方口径），故条目使用 MySQL 标准
  字典视图，并逐条标注“需在 GoldenDB V6 实测核对”。

规则：risk 只用 只读/谨慎/危险；危险操作先给只读确认查询，危险命令只以
"-- DANGER: ..." 注释模板出现，绝不留裸可执行语句。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
SCRIPTS_DIR = os.path.join(BASE, "scripts")

# 目录名（英文 slug，与 mysql 库一致）与中文大类对应
CAT_DIRS = {
    "日常巡检": "daily-check",
    "性能优化": "performance",
    "慢SQL": "slow-sql",
    "锁/会话": "lock-session",
    "空间/存储": "storage",
    "备份恢复": "backup-restore",
    "高可用/容灾": "ha",
    "用户/安全": "user-security",
}


def item(title, versions, risk, desc, sql, params, notes):
    return {"title": title, "versions": versions, "risk": risk,
            "desc": desc, "sql": sql, "params": params, "notes": notes}


def build(db_id, name, versions, note, cats):
    """cats: [(大类, 小类, [(文件名slug, item字典), ...]), ...]，按顺序编号。"""
    n = 0
    categories = []
    for cat_name, sub_name, items in cats:
        sub_items = []
        for slug, it in items:
            n += 1
            it = dict(it)
            it["id"] = "%s-%03d" % (db_id, n)
            sub_items.append(it)
            # 写 .sql 文件：内容就是 sql 字段原文
            d = os.path.join(SCRIPTS_DIR, db_id, CAT_DIRS[cat_name])
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "%02d-%s.sql" % (len(sub_items), slug)),
                      "w", encoding="utf-8") as f:
                f.write(it["sql"] + "\n")
        categories.append({"name": cat_name,
                           "subcategories": [{"name": sub_name,
                                              "items": sub_items}]})
    data = {"id": db_id, "name": name, "versions": versions, "note": note,
            "categories": categories}
    with open(os.path.join(DATA_DIR, "toolbox-%s.json" % db_id),
              "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return n


# ---------------------------------------------------------------- TDSQL
TDSQL_CATS = [
    ("日常巡检", "实例", [
        ("instance-version-uptime", item(
            "实例版本 / 运行状态", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "VERSION() / SHOW GLOBAL STATUS",
            "SELECT VERSION() AS db_version;\n"
            "SHOW GLOBAL STATUS WHERE Variable_name IN "
            "('Uptime', 'Threads_connected', 'Threads_running', 'Queries', 'Slow_queries');",
            [],
            "依据：腾讯云官方《TDSQL for MySQL Overview》，TDSQL 为分布式数据库，"
            "主从 HA 架构，兼容常用 MySQL 语法。分布式实例经 SQL 引擎/TProxy 接入，"
            "看到的是逻辑库版本与状态，各 SET（分片组）需逐个核对，需在 TDSQL MySQL版实测核对。")),
        ("shard-distribution", item(
            "分片分布 / 倾斜检查", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "分片键 GROUP BY 计数",
            "SELECT <SHARDKEY>, COUNT(*) AS row_cnt\n"
            "FROM <SCHEMA>.<TABLE>\n"
            "GROUP BY <SHARDKEY>\n"
            "ORDER BY row_cnt DESC\n"
            "LIMIT 20;",
            [{"name": "SHARDKEY", "desc": "分表键（建表时指定的 shardkey 列）"},
             {"name": "SCHEMA.TABLE", "desc": "分片表名"}],
            "依据：腾讯云官方概述，分片按 shardkey 取模打散到各 SET；"
            "单分片行数悬殊即为倾斜。GROUP BY 汇总口径（逻辑层汇总还是单分片）"
            "取决于接入方式，需在 TDSQL MySQL版实测核对。")),
    ]),
    ("性能优化", "性能", [
        ("innodb-buffer-pool-hit-rate", item(
            "InnoDB 缓冲池命中率", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "performance_schema.global_status",
            "SELECT ROUND((1 - (SELECT VARIABLE_VALUE FROM performance_schema.global_status "
            "WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') / NULLIF((SELECT VARIABLE_VALUE "
            "FROM performance_schema.global_status WHERE VARIABLE_NAME = "
            "'Innodb_buffer_pool_read_requests'), 0)) * 100, 2) AS hit_ratio_pct;",
            [],
            "依据：TDSQL 兼容 MySQL，InnoDB 为主要引擎；"
            "performance_schema.global_status 在 MySQL 5.7+ 可用。"
            "分布式下该值是当前接入 SET 的，逐 SET 对比才有意义，需在 TDSQL MySQL版实测核对。")),
        ("analyze-table-stats", item(
            "统计信息收集（ANALYZE TABLE）", "TDSQL MySQL版 5.7/8.0 分布式",
            "谨慎", "ANALYZE TABLE",
            "-- 1. 先确认表统计信息是否陈旧（只读）：\n"
            "SELECT TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH, DATA_LENGTH, INDEX_LENGTH, UPDATE_TIME\n"
            "FROM information_schema.TABLES\n"
            "WHERE TABLE_SCHEMA = '<SCHEMA>' AND TABLE_NAME = '<TABLE>';\n"
            "-- 2. 确认后再执行（建议非高峰）：\n"
            "-- DANGER: ANALYZE TABLE <SCHEMA>.<TABLE>;",
            [{"name": "SCHEMA", "desc": "库名"}, {"name": "TABLE", "desc": "表名"}],
            "依据：TDSQL 兼容 MySQL 语法。分布式表 ANALYZE 是否按分片逐个执行、"
            "是否阻塞业务，需在 TDSQL MySQL版实测核对。")),
    ]),
    ("慢SQL", "定位", [
        ("top-sql-digest", item(
            "慢SQL Top（performance_schema 摘要）", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "events_statements_summary_by_digest",
            "SELECT DIGEST_TEXT, COUNT_STAR,\n"
            "  ROUND(SUM_TIMER_WAIT / 1000000000000, 2) AS total_sec,\n"
            "  ROUND(AVG_TIMER_WAIT / 1000000000000, 4) AS avg_sec,\n"
            "  SUM_ROWS_EXAMINED\n"
            "FROM performance_schema.events_statements_summary_by_digest\n"
            "WHERE DIGEST_TEXT IS NOT NULL\n"
            "ORDER BY SUM_TIMER_WAIT DESC\n"
            "LIMIT 10;",
            [],
            "依据：TDSQL 兼容 MySQL，performance_schema 为 MySQL 标准视图。"
            "需 performance_schema 开启；分布式下摘要是逻辑层聚合还是单 SET 的，"
            "需在 TDSQL MySQL版实测核对。")),
        ("top-sql-pg-stat-statements", item(
            "慢SQL Top（PG版 pg_stat_statements）", "TDSQL PostgreSQL版 分布式/集中式",
            "只读", "pg_stat_statements",
            "SELECT query, calls,\n"
            "  ROUND(total_exec_time::numeric / 1000, 2) AS total_sec,\n"
            "  ROUND(mean_exec_time::numeric, 2) AS mean_ms, rows\n"
            "FROM pg_stat_statements\n"
            "ORDER BY total_exec_time DESC\n"
            "LIMIT 10;",
            [],
            "依据：TDSQL PostgreSQL版操作指南（腾讯云官方），该版本分分布式/集中式，"
            "CN/DN/GTM 架构。pg_stat_statements 需在 shared_preload_libraries 中加载；"
            "列名 total_exec_time 为 PG 13+，低版本为 total_time，需在 TDSQL PostgreSQL版实测核对。")),
    ]),
    ("锁/会话", "锁", [
        ("blocking-locks-long-trx", item(
            "阻塞锁 / 长事务", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "information_schema.innodb_trx",
            "SELECT trx_id, trx_state, trx_started, trx_mysql_thread_id, trx_query, trx_rows_locked\n"
            "FROM information_schema.innodb_trx\n"
            "ORDER BY trx_started\n"
            "LIMIT 20;",
            [],
            "依据：TDSQL 兼容 MySQL，information_schema.innodb_trx 为 MySQL 标准视图。"
            "MySQL 8.0 已移除 information_schema.innodb_lock_waits，改查 "
            "performance_schema.data_lock_waits；5.7 与 8.0 内核写法不同，需在 TDSQL MySQL版实测核对。")),
        ("kill-session", item(
            "杀会话（KILL）", "TDSQL MySQL版 5.7/8.0 分布式",
            "危险", "KILL",
            "-- 1. 先确认会话（只读）：\n"
            "SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO\n"
            "FROM information_schema.PROCESSLIST\n"
            "WHERE ID = <THREAD_ID>;\n"
            "-- 2. 确认无误后再执行（危险）：\n"
            "-- DANGER: KILL <THREAD_ID>;",
            [{"name": "THREAD_ID", "desc": "会话 ID（PROCESSLIST 的 ID 列）"}],
            "依据：TDSQL 兼容 MySQL，KILL 为 MySQL 标准命令。托管实例一般不提供 "
            "super user 权限，KILL 他人会话需相应权限；分布式下 KILL 只作用于当前接入的"
            "SET/节点，跨分片会话需逐节点处理，需在 TDSQL MySQL版实测核对。")),
    ]),
    ("空间/存储", "空间", [
        ("schema-size", item(
            "库空间使用率", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "information_schema.TABLES",
            "SELECT TABLE_SCHEMA,\n"
            "  ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb,\n"
            "  ROUND(SUM(DATA_LENGTH) / 1024 / 1024, 2) AS data_mb,\n"
            "  ROUND(SUM(INDEX_LENGTH) / 1024 / 1024, 2) AS index_mb\n"
            "FROM information_schema.TABLES\n"
            "GROUP BY TABLE_SCHEMA\n"
            "ORDER BY size_mb DESC;",
            [],
            "依据：TDSQL 兼容 MySQL，information_schema.TABLES 为 MySQL 标准视图。"
            "分布式下汇总口径（逻辑层汇总还是单分片）取决于接入方式，需在 TDSQL MySQL版实测核对。")),
        ("large-tables-top", item(
            "大表 Top", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "information_schema.TABLES",
            "SELECT TABLE_SCHEMA, TABLE_NAME,\n"
            "  ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb,\n"
            "  TABLE_ROWS\n"
            "FROM information_schema.TABLES\n"
            "WHERE TABLE_SCHEMA NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')\n"
            "ORDER BY DATA_LENGTH + INDEX_LENGTH DESC\n"
            "LIMIT 20;",
            [],
            "依据：TDSQL 兼容 MySQL，information_schema.TABLES 为 MySQL 标准视图。"
            "分片倾斜另见 tdsql-002；单表过大时结合分片键重分布，需在 TDSQL MySQL版实测核对。")),
    ]),
    ("备份恢复", "备份", [
        ("backup-binlog-status", item(
            "备份 / Binlog 状态检查", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "SHOW BINARY LOGS / SHOW MASTER STATUS",
            "SHOW BINARY LOGS;\n"
            "SHOW MASTER STATUS;\n"
            "SHOW VARIABLES LIKE 'binlog_format';",
            [],
            "依据：腾讯云官方《Backup Mode》，TDSQL MySQL版支持全量备份与基于 binlog 的"
            "增量备份，保留期默认 7 天（1-365 天可配），备份与回档在控制台操作，"
            "无单条 SQL 可查备份集；SHOW BINARY LOGS 只能看 binlog 清单，需在 TDSQL MySQL版实测核对。")),
        ("pitr-rollback-drill", item(
            "时间点恢复 / 回档演练清单", "TDSQL MySQL版 5.7/8.0 分布式；PG版",
            "危险", "控制台回档（无 SQL）",
            "-- 1. 先确认备份与 binlog（只读，见 tdsql-011）。\n"
            "-- 2. 回档为控制台操作（危险，先在测试实例演练）：\n"
            "-- DANGER: 控制台 → 备份恢复 → 按备份文件回档，或按时间点回档到原实例 / 克隆到新实例；\n"
            "-- DANGER: TDSQL PostgreSQL版只支持整实例回档并生成新实例，不支持指定库/表回档。",
            [],
            "依据：腾讯云官方《Backup Mode》（MySQL版全量+增量、按时间点回档）与"
            "《TDSQL PostgreSQL版 操作指南》（只支持整实例回档生成新实例）。"
            "生产回档前务必先停写并做副本，需在 TDSQL 实测核对。")),
    ]),
    ("高可用/容灾", "容灾", [
        ("replication-delay", item(
            "主备复制延迟", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "SHOW REPLICA STATUS / SHOW SLAVE STATUS",
            "SHOW REPLICA STATUS;\n"
            "-- MySQL 5.7 / TDSQL 5.7 内核用：SHOW SLAVE STATUS;",
            [],
            "依据：腾讯云官方概述，TDSQL 默认主从 HA 架构；SHOW REPLICA STATUS 为 MySQL 8.0+ "
            "写法，5.7 用 SHOW SLAVE STATUS。看 Seconds_Behind_Master、IO/SQL 线程状态；"
            "分布式下各 SET 复制状态需逐 SET 查，需在 TDSQL MySQL版实测核对。")),
    ]),
    ("用户/安全", "安全", [
        ("users-grants", item(
            "用户列表 / 权限", "TDSQL MySQL版 5.7/8.0 分布式",
            "只读", "mysql.user / SHOW GRANTS",
            "SELECT User, Host FROM mysql.user ORDER BY User, Host;\n"
            "SHOW GRANTS FOR '<USER>'@'<HOST>';",
            [{"name": "USER", "desc": "用户名"}, {"name": "HOST", "desc": "主机（% 或 IP）"}],
            "依据：TDSQL 兼容 MySQL，mysql.user 为 MySQL 标准系统表。云上托管实例一般不提供 "
            "super user 权限（TDSQL PostgreSQL版操作指南明确；MySQL版以控制台账号管理为准），"
            "不要修改默认账号信息，需在 TDSQL MySQL版实测核对。")),
    ]),
]

# ---------------------------------------------------------------- GoldenDB
GOLDENDB_CATS = [
    ("日常巡检", "实例", [
        ("instance-version-uptime", item(
            "实例版本 / 运行状态", "GoldenDB V6 分布式/集中式",
            "只读", "VERSION() / SHOW GLOBAL STATUS",
            "SELECT VERSION() AS db_version;\n"
            "SHOW GLOBAL STATUS WHERE Variable_name IN "
            "('Uptime', 'Threads_connected', 'Threads_running', 'Queries', 'Slow_queries');",
            [],
            "依据：GoldenDB V6 技术白皮书（中兴通讯官方），DN 基于 MySQL 内核、"
            "兼容 MySQL 语法与协议。经 CN（计算节点/DBProxy）接入时返回的是 CN 侧逻辑版本"
            "还是 DN 版本、状态口径，需在 GoldenDB V6 实测核对。")),
        ("shard-table-definition", item(
            "分片表定义检查", "GoldenDB V6 分布式",
            "只读", "SHOW CREATE TABLE",
            "SHOW CREATE TABLE <SCHEMA>.<TABLE>;",
            [{"name": "SCHEMA.TABLE", "desc": "表名"}],
            "依据：GoldenDB V6 技术白皮书，支持 Range/Hash/List 三种水平分片规则、"
            "DUPLICATE 复制表、分片之上再做本地分区。SHOW CREATE TABLE 用于核对分片键与"
            "分片规则是否与设计一致，需在 GoldenDB V6 实测核对。")),
    ]),
    ("性能优化", "性能", [
        ("innodb-buffer-pool-hit-rate", item(
            "InnoDB 缓冲池命中率", "GoldenDB V6 分布式/集中式",
            "只读", "performance_schema.global_status",
            "SELECT ROUND((1 - (SELECT VARIABLE_VALUE FROM performance_schema.global_status "
            "WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') / NULLIF((SELECT VARIABLE_VALUE "
            "FROM performance_schema.global_status WHERE VARIABLE_NAME = "
            "'Innodb_buffer_pool_read_requests'), 0)) * 100, 2) AS hit_ratio_pct;",
            [],
            "依据：GoldenDB DN 为 MySQL 内核，performance_schema.global_status 为 MySQL 标准视图。"
            "该查询应在 DN 上执行，CN 上不一定透传，需在 GoldenDB V6 实测核对。")),
        ("analyze-table-stats", item(
            "统计信息收集（ANALYZE TABLE）", "GoldenDB V6 分布式/集中式",
            "谨慎", "ANALYZE TABLE",
            "-- 1. 先确认表统计信息是否陈旧（只读）：\n"
            "SELECT TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH, DATA_LENGTH, INDEX_LENGTH, UPDATE_TIME\n"
            "FROM information_schema.TABLES\n"
            "WHERE TABLE_SCHEMA = '<SCHEMA>' AND TABLE_NAME = '<TABLE>';\n"
            "-- 2. 确认后再执行（建议非高峰）：\n"
            "-- DANGER: ANALYZE TABLE <SCHEMA>.<TABLE>;",
            [{"name": "SCHEMA", "desc": "库名"}, {"name": "TABLE", "desc": "表名"}],
            "依据：GoldenDB DN 兼容 MySQL 语法。分布式表 ANALYZE 是否按分片逐个执行、"
            "是否阻塞业务，需在 GoldenDB V6 实测核对。")),
    ]),
    ("慢SQL", "定位", [
        ("top-sql-digest", item(
            "慢SQL Top（performance_schema 摘要）", "GoldenDB V6 分布式/集中式",
            "只读", "events_statements_summary_by_digest",
            "SELECT DIGEST_TEXT, COUNT_STAR,\n"
            "  ROUND(SUM_TIMER_WAIT / 1000000000000, 2) AS total_sec,\n"
            "  ROUND(AVG_TIMER_WAIT / 1000000000000, 4) AS avg_sec,\n"
            "  SUM_ROWS_EXAMINED\n"
            "FROM performance_schema.events_statements_summary_by_digest\n"
            "WHERE DIGEST_TEXT IS NOT NULL\n"
            "ORDER BY SUM_TIMER_WAIT DESC\n"
            "LIMIT 10;",
            [],
            "依据：GoldenDB DN 为 MySQL 内核，performance_schema 为 MySQL 标准视图。"
            "经 CN 看到的是 CN 侧聚合还是单 DN 的摘要、是否需逐 DN 查，需在 GoldenDB V6 实测核对。")),
        ("explain-plan", item(
            "执行计划（EXPLAIN）", "GoldenDB V6 分布式/集中式",
            "只读", "EXPLAIN",
            "EXPLAIN SELECT * FROM <SCHEMA>.<TABLE> WHERE <CONDITION>;",
            [{"name": "SCHEMA.TABLE", "desc": "表名"},
             {"name": "CONDITION", "desc": "WHERE 条件"}],
            "依据：GoldenDB DN 兼容 MySQL 语法，EXPLAIN 为 MySQL 标准命令。CN 会把 SQL 下发到"
            "各 DN 再汇总结果，跨分片 JOIN 的计划以 CN 侧为准，需在 GoldenDB V6 实测核对。")),
    ]),
    ("锁/会话", "锁", [
        ("blocking-locks-long-trx", item(
            "阻塞锁 / 长事务", "GoldenDB V6 分布式/集中式",
            "只读", "information_schema.innodb_trx",
            "SELECT trx_id, trx_state, trx_started, trx_mysql_thread_id, trx_query, trx_rows_locked\n"
            "FROM information_schema.innodb_trx\n"
            "ORDER BY trx_started\n"
            "LIMIT 20;",
            [],
            "依据：GoldenDB DN 为 MySQL 内核，information_schema.innodb_trx 为 MySQL 标准视图。"
            "MySQL 8.0 已移除 information_schema.innodb_lock_waits，改查 "
            "performance_schema.data_lock_waits；DN 内核版本不同写法不同，需在 GoldenDB V6 实测核对。")),
        ("kill-session", item(
            "杀会话（KILL）", "GoldenDB V6 分布式/集中式",
            "危险", "KILL",
            "-- 1. 先确认会话（只读）：\n"
            "SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO\n"
            "FROM information_schema.PROCESSLIST\n"
            "WHERE ID = <THREAD_ID>;\n"
            "-- 2. 确认无误后再执行（危险）：\n"
            "-- DANGER: KILL <THREAD_ID>;",
            [{"name": "THREAD_ID", "desc": "会话 ID（PROCESSLIST 的 ID 列）"}],
            "依据：GoldenDB DN 兼容 MySQL 语法，KILL 为 MySQL 标准命令。跨分片事务的会话"
            "可能涉及多个 DN 与 GTM 协调，杀会话前务必确认业务影响，需在 GoldenDB V6 实测核对。")),
    ]),
    ("空间/存储", "空间", [
        ("schema-size", item(
            "库空间使用率", "GoldenDB V6 分布式/集中式",
            "只读", "information_schema.TABLES",
            "SELECT TABLE_SCHEMA,\n"
            "  ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb,\n"
            "  ROUND(SUM(DATA_LENGTH) / 1024 / 1024, 2) AS data_mb,\n"
            "  ROUND(SUM(INDEX_LENGTH) / 1024 / 1024, 2) AS index_mb\n"
            "FROM information_schema.TABLES\n"
            "GROUP BY TABLE_SCHEMA\n"
            "ORDER BY size_mb DESC;",
            [],
            "依据：GoldenDB DN 为 MySQL 内核，information_schema.TABLES 为 MySQL 标准视图。"
            "经 CN 汇总还是单 DN 口径，需在 GoldenDB V6 实测核对。")),
        ("shard-distribution", item(
            "分片数据分布 / 倾斜检查", "GoldenDB V6 分布式",
            "只读", "分片键 GROUP BY 计数",
            "SELECT <SHARDKEY>, COUNT(*) AS row_cnt\n"
            "FROM <SCHEMA>.<TABLE>\n"
            "GROUP BY <SHARDKEY>\n"
            "ORDER BY row_cnt DESC\n"
            "LIMIT 20;",
            [{"name": "SHARDKEY", "desc": "分片键列"},
             {"name": "SCHEMA.TABLE", "desc": "分片表名"}],
            "依据：GoldenDB V6 技术白皮书，数据按分片键分布在不同分片组，支持在线新增分片"
            "与数据重分布。单分片行数悬殊即为倾斜，需重分布；分布口径需在 GoldenDB V6 实测核对。")),
    ]),
    ("备份恢复", "备份", [
        ("backup-binlog-status", item(
            "备份 / Binlog 状态检查", "GoldenDB V6 分布式/集中式",
            "只读", "SHOW BINARY LOGS / SHOW MASTER STATUS",
            "SHOW BINARY LOGS;\n"
            "SHOW MASTER STATUS;\n"
            "SHOW VARIABLES LIKE 'binlog_format';",
            [],
            "依据：GoldenDB V6 技术白皮书，支持逻辑备份与物理备份、按时间点恢复，"
            "备份通过 OMM/Insight 或 MySQL 生态工具执行，无单条 SQL 可查备份集；"
            "SHOW BINARY LOGS 只能看 binlog 清单，需在 GoldenDB V6 实测核对。")),
        ("pitr-restore-drill", item(
            "时间点恢复演练清单", "GoldenDB V6 分布式/集中式",
            "危险", "OMM/Insight 恢复（无 SQL）",
            "-- 1. 先确认备份与 binlog（只读，见 goldendb-011）。\n"
            "-- 2. 恢复为 OMM/Insight 操作（危险，先在测试集群演练）：\n"
            "-- DANGER: OMM/Insight → 备份恢复 → 选择备份集 → 按时间点恢复到目标集群，"
            "配合 LoadServer（LDS）做数据装载；恢复前先停写并做副本。",
            [],
            "依据：GoldenDB V6 技术白皮书，支持按时间点恢复，LoadServer（LDS）负责数据装载"
            "与迁移，运维通过 Insight/OMM 执行。生产恢复前务必先在测试集群演练，需在 GoldenDB V6 实测核对。")),
    ]),
    ("高可用/容灾", "容灾", [
        ("shard-group-replication", item(
            "分片组主备复制状态", "GoldenDB V6 分布式",
            "只读", "SHOW REPLICA STATUS / SHOW SLAVE STATUS",
            "SHOW REPLICA STATUS;\n"
            "-- DN 内核为 MySQL 5.7 时用：SHOW SLAVE STATUS;",
            [],
            "依据：GoldenDB V6 技术白皮书，每个分片组（DBGroup）由一主多备组成，"
            "备机以强同步方式复制主库日志，主库故障时分片组内自动选举切换。SQL 只能在直连 DN 时"
            "看复制状态，CN 上不可见；主备切换走 Insight/OMM，不要直接在 DN 上改，需在 GoldenDB V6 实测核对。")),
    ]),
    ("用户/安全", "安全", [
        ("users-grants", item(
            "用户列表 / 权限", "GoldenDB V6 分布式/集中式",
            "只读", "mysql.user / SHOW GRANTS",
            "SELECT User, Host FROM mysql.user ORDER BY User, Host;\n"
            "SHOW GRANTS FOR '<USER>'@'<HOST>';",
            [{"name": "USER", "desc": "用户名"}, {"name": "HOST", "desc": "主机（% 或 IP）"}],
            "依据：GoldenDB DN 为 MySQL 内核，mysql.user 为 MySQL 标准系统表。白皮书："
            "一套物理集群可划分 sys_cluster 系统租户与多个业务租户，各租户元数据隔离；"
            "租户级账号以 OMM 为准，需在 GoldenDB V6 实测核对。")),
    ]),
]

if __name__ == "__main__":
    n1 = build("tdsql", "TDSQL",
               "TDSQL MySQL版 5.7/8.0 分布式；TDSQL PostgreSQL版 分布式/集中式",
               "腾讯云 TDSQL：MySQL版（DCDB）分布式 + PostgreSQL版分布式/集中式；"
               "官方文档见 cloud.tencent.com/document/product/1042，未在真实环境跑过，见各条 notes",
               TDSQL_CATS)
    n2 = build("goldendb", "GoldenDB", "GoldenDB V6 分布式/集中式/混合部署",
               "中兴 GoldenDB V6：DN 为 MySQL 内核，CN/GTM/管理节点分布式架构；"
               "官方白皮书见 zte.com.cn，未找到公开 SQL 手册，未在真实环境跑过，见各条 notes",
               GOLDENDB_CATS)
    print("tdsql:", n1, "goldendb:", n2, "total:", n1 + n2)
