# DBA 工具箱 · uTools 插件

一个给 DBA 用的本地工具箱：**SQL 格式化 / 方言互转 / 脱敏 + 215 条主流数据库常用脚本**，按数据库、分层、适用版本分类，开箱即用。

作者：5 年+ DBA，Oracle OCP（11g）+ MySQL 8.0 OCP，Oracle RAC / DG / OGG、MySQL MGR / MHA / 主从、SQL Server AlwaysOn、达梦 / OceanBase / GBase 国产化迁移。

> ⚠️ **安全声明**：本仓库**不连数据库、不存密码、不上传任何内容**。所有脚本都在本机处理，危险操作（KILL 会话、恢复、切换、DDL）只给命令模板 + 二次确认，执行前请先在测试库验证。部分脚本需对应授权（如 Oracle Diagnostic / Tuning Pack）或第三方工具（如 MHA、XtraBackup、binlog2sql），文件头已注明。

## 内容总览

| 数据库 | 适用版本 | 条数 |
|---|---|---|
| Oracle | 11gR2 / 12c / 19c / 21c / 23ai | 62 |
| MySQL | 5.7 / 8.0 / 8.4 LTS | 45 |
| PostgreSQL | 12–17 | 26 |
| SQL Server | 2016 / 2019 / 2022 | 20 |
| 达梦 DM8 | DM8 / 8.1 | 16 |
| OceanBase | 3.x / 4.x（MySQL / Oracle 模式） | 16 |
| GBase 8a / 8s | 8a MPP / 8s OLTP | 9 |
| TiDB | 6.x / 7.x / 8.x | 10 |
| 通用 / 跨库 | 全库通用 | 11 |
| **合计** | | **215** |

每库统一 8 个大类：日常巡检、性能优化、慢 SQL、锁 / 会话、空间 / 存储、备份恢复、高可用 / 容灾、用户 / 安全。

风险分三档：**只读**（SELECT / 查询类，可直接跑）、**谨慎**（备份 / 统计 / 配置类，建议非高峰 + 先在测试库跑）、**危险**（KILL / 恢复 / 切换 / DDL 类，必须先确认业务影响）。

## 目录结构

```
.
├── plugin.json              # uTools 插件配置：main / preload / features
├── preload.js               # uTools preload（CommonJS，Node v20.19.1）
├── index.html               # uTools 插件主界面（无框架、无构建）
├── lib/sql-core.js          # SQL 格式化 / 互转 / 脱敏核心（preload 与前端共用）
├── logo.png
├── data/
│   ├── toolbox.json         # 清单（215 条，无 SQL）
│   ├── toolbox-filled.json  # 完整数据：每条含 sql / params / notes，插件直接读这个
│   └── toolbox-<db>.json    # 按库拆分：oracle / mysql / postgres / sqlserver / dameng / oceanbase / gbase / tidb / common
├── docs/
│   └── DBA_TOOLBOX_LIST.md  # 完整清单：数据库 > 大类 > 小类 > 脚本 | 版本 | 风险
├── scripts/                 # 215 个 .sql 文件，一条一个文件
│   ├── oracle/日常巡检/01-*.sql
│   ├── mysql/daily-check/01-*.sql
│   ├── postgres/...
│   ├── sqlserver/...
│   ├── dameng/...  oceanbase/...  gbase/...  tidb/...  common/...
└── build_*.py               # 清单与 SQL 的生成脚本，可复跑核对
```

## uTools 插件怎么用（v0.1 已实现）

1. uTools 里搜 `开发者工具` 安装，打开后添加本地插件，选本仓库文件夹
2. `Alt+空格` 输入 `SQL格式化` / `sql` / `dba` 回车
3. 选中 SQL 后鼠标中键呼出超级面板，选「格式化这段 SQL」；也可以把 SQL 粘贴进 uTools 输入框匹配，或拖 `.sql` 文件进来

插件已实现的功能：
- SQL 格式化（关键字大写可选，2/4 空格缩进，子查询换行）
- Oracle ↔ MySQL 方言互转（NVL↔IFNULL、SYSDATE↔NOW()、TO_CHAR↔DATE_FORMAT 等，规则式，带警告）
- SQL 脱敏（字符串 → `***`，数字 → `?`）
- 列表转 IN（自动去重，纯数字不加引号，>1000 提示 ORA-01795）
- 时间戳互转（10 位秒 / 13 位毫秒 ↔ 日期）

脚本库（`scripts/` + `data/toolbox-filled.json`）是下一步要接进插件搜索界面的数据源，当前版本先以文件形式提供。

## 脚本怎么用

```bash
# 按库、按大类找文件，例如 Oracle 慢 SQL：
ls scripts/oracle/慢SQL/
# 每个文件头都写了标题、适用版本、风险、说明，先看头再跑
head -20 scripts/oracle/慢SQL/01-*.sql
```

占位符说明：文件里的 `<schema>`、`<table_name>`、`<sid>`、`<backup_dir>` 等是占位符，替换成你自己的值再执行；`<...>` 不替换直接跑会报错，这是故意的，防止误执行。

## 已知未实测项（请按 notes 核对）

- Oracle：自动索引、SQL Tuning 建议需 Tuning Pack 授权；AWR/ASH 需 Diagnostic Pack；OGG、告警日志路径随版本/环境而变
- MySQL：`SHOW SLAVE STATUS` 在 8.4 已移除（用 `SHOW REPLICA STATUS`）；`mysqldump --master-data=2` 在 8.4 改名 `--source-data=2`；MHA、binlog2sql 未实测
- PostgreSQL：`pg_stat_statements` 列名 12 与 13+ 不同；`pg_stat_wal` 仅 14+；bloat / hypopg 需另装扩展
- 国产库（达梦 / OceanBase / GBase / TiDB）：部分 `V$` / `GV$` / 系统表列名未在真实库实测，`notes` 里写了“需在对应版本实测核对”

欢迎提 Issue / PR 纠错：请注明数据库、版本、报错原文。

## 开源协议

MIT License，见 [LICENSE](LICENSE)。
