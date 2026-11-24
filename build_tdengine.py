#!/usr/bin/env python3
"""Generate TDengine toolbox data (14 items) + per-item .sql files.

Sources (official docs, docs.tdengine.com / tdengine.com):
- Databases (CREATE/ALTER DATABASE: KEEP/DURATION/COMP/REPLICA/RETENTIONS):
  https://docs.tdengine.com/reference/taos-sql/database/
- Data Model (CREATE STABLE / CREATE TABLE ... USING / one-table-per-device):
  https://docs.tdengine.com/2.6/develop/model/  (syntax unchanged in 3.x)
- Data Backup and Restoration (CREATE FULL BACKUP / SHOW BACKUPS / taosd --restore, Enterprise):
  https://docs.tdengine.com/operations-and-tooling/operations/backup/
- taosdump Reference: https://docs.tdengine.com/operations-and-tooling/tools/taosdump/
- TSDB Compression (COMP, ins_databases db_name/data_size/storage_size/compression_ratio):
  https://tdengine.com/tsdb-compression-and-storage-cost-optimization/
- Architecture (dnodes/mnodes/vnodes/vgroups/qnodes/snodes, SHOW DNODES):
  https://tdengine.com/tsdb-architecture-core-technology-explained/
- 3.4.1.0 Release Notes (SHOW QUERIES shows execution progress):
  https://docs.tdengine.com/release-history/notes/3.4.1.0/
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DB = "tdengine"

# (category, subcategory, dir, slug, title, versions, risk, desc, sql, params, notes)
ITEMS = [
    ("日常巡检", "集群", "日常巡检", "version-dnodes",
     "版本与数据节点状态", "3.x", "只读", "SELECT SERVER_VERSION() / SHOW DNODES",
     "SELECT SERVER_VERSION();\nSHOW DNODES;\nSHOW MNODES;",
     [],
     "依据：TDengine 官方架构文档（dnode 为 taosd 进程、mnode 管元数据与协调）。SERVER_VERSION() 列名与 SHOW DNODES 输出列需在 3.x 实测核对。"),
    ("日常巡检", "集群", "日常巡检", "databases-stables-count",
     "库 / 超级表清单", "3.x", "只读", "SHOW DATABASES / SHOW STABLES",
     "SHOW DATABASES;\nUSE <DBNAME>;\nSHOW STABLES;\nSHOW TABLES;",
     [{"name": "DBNAME", "desc": "数据库名"}],
     "依据：TDengine 官方文档 SHOW 语法。SHOW STABLES / SHOW TABLES 需先 USE 指定库；输出列需在 3.x 实测核对。"),
    ("性能/写入", "查询", "性能-写入", "show-queries",
     "正在执行的查询", "3.4+", "只读", "SHOW QUERIES",
     "SHOW QUERIES;",
     [],
     "依据：TDengine 3.4.1.0 Release Notes（SHOW QUERIES 显示执行进度）。输出列（如 query id / 执行时长）需在 3.4.x 实测核对。"),
    ("性能/写入", "查询", "性能-写入", "interval-aggregation",
     "超级表下采样聚合（INTERVAL）", "3.x", "只读", "INTERVAL / PARTITION BY tbname",
     "SELECT _wstart AS window_start, tbname, count(*) AS rows_cnt, avg(<MEASURE_COL>) AS avg_val\nFROM <STABLE>\nWHERE ts >= now - 1h AND ts < now\nPARTITION BY tbname INTERVAL(5m)\nORDER BY window_start DESC, tbname LIMIT 100;",
     [{"name": "STABLE", "desc": "超级表名"}, {"name": "MEASURE_COL", "desc": "度量列名，如 current"}],
     "依据：TDengine 官方文档的时序扩展语法（INTERVAL 时间窗口、PARTITION BY tbname 按子表分组）。_wstart 为窗口起始时间伪列，需在 3.x 实测核对。"),
    ("慢查询", "定位", "慢查询", "slow-query-show-queries",
     "慢查询定位（SHOW QUERIES + EXPLAIN）", "3.x", "只读", "SHOW QUERIES / EXPLAIN",
     "-- 1. 先看当前在跑的查询（只读）：\nSHOW QUERIES;\n-- 2. 对可疑 SQL 看执行计划（模板，替换为真实 SQL）：\nEXPLAIN SELECT * FROM <STABLE> WHERE ts >= now - 1h;",
     [{"name": "STABLE", "desc": "超级表名"}],
     "依据：TDengine 官方文档（SHOW QUERIES、EXPLAIN）。TDengine 的慢查询日志阈值与输出位置由服务端配置决定，本条未编参数名，需在 3.x 实测核对 slowLog 相关配置。"),
    ("慢查询", "定位", "慢查询", "last-row-check",
     "最新数据到达检查（LAST_ROW）", "3.x", "只读", "LAST_ROW",
     "SELECT LAST_ROW(*) FROM <STABLE>;\nSELECT tbname, LAST_ROW(ts) AS last_ts, now - LAST_ROW(ts) AS lag\nFROM <STABLE> PARTITION BY tbname ORDER BY lag DESC LIMIT 20;",
     [{"name": "STABLE", "desc": "超级表名"}],
     "依据：TDengine 官方文档的 LAST_ROW 函数（取每子表最新一行，常用于判断设备断流）。PARTITION BY tbname + LAST_ROW 的组合写法需在 3.x 实测核对。"),
    ("空间/压缩", "空间", "空间-压缩", "database-size-compression",
     "库空间与压缩率", "3.x", "只读", "information_schema.ins_databases",
     "SELECT db_name, data_size, storage_size,\n  round(data_size * 1.0 / NULLIF(storage_size, 0), 2) AS compression_ratio\nFROM information_schema.ins_databases ORDER BY storage_size DESC;",
     [],
     "依据：TDengine 官方压缩指南（SELECT db_name, compression_ratio FROM information_schema.ins_databases；data_size / storage_size 同文）。列名需在 3.x 实测核对。"),
    ("空间/压缩", "空间", "空间-压缩", "vgroups-distribution",
     "虚拟组与子表分布", "3.x", "只读", "SHOW VGROUPS / SHOW TABLES",
     "SHOW VGROUPS;\nUSE <DBNAME>;\nSHOW TABLES;",
     [{"name": "DBNAME", "desc": "数据库名"}],
     "依据：TDengine 官方架构文档（vgroup 为一组互为副本的 vnode）。SHOW VGROUPS 输出列需在 3.x 实测核对。"),
    ("保留策略", "保留", "保留策略", "show-create-database",
     "库保留参数查看", "3.x", "只读", "SHOW CREATE DATABASE",
     "SHOW CREATE DATABASE <DBNAME>;",
     [{"name": "DBNAME", "desc": "数据库名"}],
     "依据：TDengine 官方 Databases 文档（KEEP / DURATION / COMP 等建库参数）。SHOW CREATE DATABASE 的输出格式需在 3.x 实测核对。"),
    ("保留策略", "保留", "保留策略", "alter-database-keep-comp",
     "修改保留时长与压缩", "3.x", "谨慎", "ALTER DATABASE KEEP / COMP",
     "-- 1. 先确认当前参数（只读）：\nSHOW CREATE DATABASE <DBNAME>;\n-- 2. 确认后再执行（KEEP 须 >= 3 倍 DURATION，缩短 KEEP 会丢弃过期数据）：\n-- DANGER: ALTER DATABASE <DBNAME> KEEP <KEEP> COMP <COMP>;",
     [{"name": "DBNAME", "desc": "数据库名"}, {"name": "KEEP", "desc": "保留时长，如 365d"}, {"name": "COMP", "desc": "压缩级别 0/1/2"}],
     "依据：TDengine 官方 Databases 文档（KEEP 默认 3650 天、须 >= 3 倍 DURATION；COMP 0 不压缩、1 一级、2 二级）。ALTER DATABASE 支持 KEEP / COMP 的写法需在 3.x 实测核对；缩短 KEEP 会删除数据，务必先确认。"),
    ("备份恢复", "备份", "备份恢复", "taosdump-logical-backup",
     "逻辑备份（taosdump）", "3.x", "谨慎", "taosdump",
     "-- shell: taosdump -h <HOST> -D <DBNAME> -o <OUTDIR>\n-- shell: taosdump -h <HOST> -A -o <OUTDIR>\n-- shell: taosdump -h <HOST> -D <DBNAME> -s -o <OUTDIR>\n-- 恢复（逻辑恢复，不覆盖已存在的表结构）：\n-- shell: taosdump -h <HOST> -i <OUTDIR>",
     [{"name": "HOST", "desc": "TDengine 服务地址"}, {"name": "DBNAME", "desc": "数据库名"}, {"name": "OUTDIR", "desc": "备份输出目录（须为空或不存在）"}],
     "依据：TDengine 官方 taosdump 文档（-D 指定库、-A 全库、-s 仅元数据、-i 恢复；3.4.2+ 支持 binary/parquet 格式）。taosdump 为逻辑备份，不含集群拓扑与配置。"),
    ("备份恢复", "备份", "备份恢复", "full-backup-restore",
     "企业版全备与恢复", "3.x 企业版", "危险", "CREATE FULL BACKUP / taosd --restore",
     "-- 1. 先查看备份记录（只读）：\nSHOW BACKUPS;\n-- 2. 全量备份（仅企业版，联机执行）：\n-- DANGER: CREATE FULL BACKUP ON DNODE <DNODE_ID> TO '<BACKUP_PATH>';\n-- 3. 恢复为离线危险操作，先在测试环境演练：\n-- DANGER: taosd --restore <BACKUP_CHAIN_PATH> --verify=1",
     [{"name": "DNODE_ID", "desc": "数据节点 ID"}, {"name": "BACKUP_PATH", "desc": "备份路径"}, {"name": "BACKUP_CHAIN_PATH", "desc": "备份链路径"}],
     "依据：TDengine 官方备份恢复文档（CREATE FULL BACKUP / SHOW BACKUPS / taosd --restore）。全备与恢复为企业版功能，社区版不可用；恢复仅还原 mnode/vnode/snode 数据，恢复前务必先停写并做副本，需在 3.x 企业版实测核对。"),
    ("高可用", "集群", "高可用", "ha-nodes-replica",
     "节点与副本状态", "3.x", "只读", "SHOW DNODES / SHOW MNODES / SHOW VGROUPS",
     "SHOW DNODES;\nSHOW MNODES;\nSHOW VGROUPS;\nSHOW CREATE DATABASE <DBNAME>;",
     [{"name": "DBNAME", "desc": "数据库名"}],
     "依据：TDengine 官方架构文档（mnode 多副本 Raft、vgroup 副本组）与 Databases 文档（REPLICA 参数：社区版为 1 或 3，2 副本为 3.3.0.0+ 企业版）。副本数以 SHOW CREATE DATABASE 输出为准，需在 3.x 实测核对。"),
    ("用户/安全", "用户", "用户-安全", "users-and-grants",
     "用户与授权", "3.x", "谨慎", "SHOW USERS / CREATE USER",
     "-- 1. 先查看现有用户（只读）：\nSHOW USERS;\n-- 2. 新建用户（模板）：\n-- DANGER: CREATE USER <USERNAME> PASS '<PASSWORD>';\n-- 3. 授权示例（语法按手册核对）：\n-- DANGER: GRANT WRITE ON <DBNAME> TO <USERNAME>;",
     [{"name": "USERNAME", "desc": "用户名"}, {"name": "PASSWORD", "desc": "密码"}, {"name": "DBNAME", "desc": "数据库名"}],
     "依据：TDengine 官方文档（SHOW USERS / CREATE USER）。GRANT 的权限关键字与对象写法需在 3.x 实测核对；切勿在脚本里留真实密码。"),
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
    n = 0
    for cat in order:
        for sub in cats[cat]["subcategories"]:
            for it in sub["items"]:
                n += 1
                it["id"] = f"{DB}-{n:03d}"
    data = {"id": DB, "name": "TDengine", "versions": "3.x（社区版 / 企业版）",
            "note": "时序数据库，一设备一表 + 超级表（STable）模型；全备为企业版功能",
            "categories": [cats[c] for c in order]}
    os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
    with open(os.path.join(BASE, "data", f"toolbox-{DB}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    counters = {}
    for cat, sub, d, slug, title, vers, risk, desc, sql, params, notes in ITEMS:
        counters[d] = counters.get(d, 0) + 1
        outdir = os.path.join(BASE, "scripts", DB, d)
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, f"{counters[d]:02d}-{slug}.sql"), "w", encoding="utf-8") as f:
            f.write(sql + "\n")
    print(f"{DB}: {n} items written")

if __name__ == "__main__":
    build()
