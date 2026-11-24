# DBA 工具箱 · 清单 v0.3（v0.2 215 条 + v0.3 新增 112 条）

- 更新：2026-11-24 · 总计 **327** 条脚本/命令 · 结构：数据库 > 大类 > 小类 > 脚本
- 风险：**只读**=SELECT/查询类，可直接跑；**谨慎**=备份/统计/配置类，建议非高峰+先在测试库跑；**危险**=KILL/恢复/切换/DDL类，必须先确认业务影响
- 版本标注：`11g+` = 11gR2 及以上，`12c+` = 12c 及以上，`8.0+` = 8.0 及以上，以此类推
- 原则：插件本身不连数据库、不存密码、不上传。所有脚本先以只读查询呈现，危险操作只给命令模板+二次确认。

## 总览

| 数据库 | 适用版本 | 条数 | 你的定位 |
|---|---|---|---|
| Oracle | 11gR2 / 12c / 19c / 21c / 23ai | 62 | 你的主力，OCP 11g，RAC/DG/OGG |
| MySQL | 5.7 / 8.0 / 8.4 LTS | 45 | 主力，MySQL 8.0 OCP，MGR/MHA/主从 |
| PostgreSQL | 12 / 13 / 14 / 15 / 16 / 17 | 26 | PCA 考证中，主力扩展方向 |
| SQL Server | 2016 / 2019 / 2022 | 20 | AlwaysOn 方向 |
| 达梦 DM8 | DM8 / DM8.1 | 16 | 国产化迁移方向，GCA/YCA 相关 |
| OceanBase | 3.x / 4.x（MySQL模式 / Oracle模式） | 16 | OBCA 考证中，国产化方向 |
| GBase 8a / 8s | 8a MPP / 8s OLTP | 9 | GBase GCA，国产化方向 |
| TiDB | 6.x / 7.x / 8.x | 10 | MySQL 兼容分布式，扩展方向 |
| 通用 / 跨库工具 | 全库通用 | 11 | 不连库的本地工具，uTools 插件 v0.1 已有部分 |
| 金仓 KingBaseES | KES V9 / V8.6 | 14 | 国产化，墨天轮第 2 |
| PolarDB | MySQL 5.7 / 8.0；PG 11/14/15/16/17 | 14 | 阿里云，墨天轮第 4 |
| GoldenDB | V6（MySQL 内核兼容） | 14 | 中兴，墨天轮第 5 |
| TDSQL | MySQL 版 / PG 版 | 14 | 腾讯云，墨天轮第 7 |
| GaussDB | 集中式 / 分布式 | 14 | 华为云，墨天轮第 9 |
| TDengine | 3.x | 14 | 时序，墨天轮第 10 |
| 崖山 YashanDB | 23.2 | 14 | 国产化，墨天轮第 11 |
| openGauss | 5.0 / 6.0 LTS | 14 | 开源 PG 内核，墨天轮第 13 |

## 分层结构示例

```
Oracle
└── 性能优化
    ├── AWR / ASH
    │   ├── 生成 AWR 快照 / 报告（11g+，只读）
    │   └── ASH Top 等待事件（11g+，只读）
    └── 慢SQL
        ├── Top SQL by Elapsed Time（11g+，只读）
        └── 执行计划 DBMS_XPLAN（11g+，只读）
```

## Oracle（62 条）· 11gR2 / 12c / 19c / 21c / 23ai

> 你的主力，OCP 11g，RAC/DG/OGG

### 日常巡检

#### 实例与版本

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例状态 / 版本 / 启动时间 | 11g+ | 只读 | v$instance, v$database |
| 监听与服务状态 | 11g+ | 只读 | lsnrctl status / srvctl status |
| 数据库 / PDB 列表 | 12c+ | 只读 | CDB+PDB，11g无PDB |
| 无效对象清单 | 11g+ | 只读 | dba_objects status=INVALID |
| 定时任务 / 作业状态 | 11g+ | 只读 | dba_scheduler_jobs |
| 告警日志近24h错误 | 11g+ | 只读 | 需读alert log / ADRCI |

#### 健康指标

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 表空间使用率 Top | 11g+ | 只读 | >85%预警 |
| 归档日志生成量 / 切换频率 | 11g+ | 只读 | v$archived_log |
| 临时表空间使用 | 11g+ | 只读 | v$tempseg_usage |
| UNDO 使用与保留 | 11g+ | 只读 | v$undostat |

### 性能优化

#### AWR / ASH

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 生成 AWR 快照 / 报告 | 11g+ | 只读 | awrrpt.sql，需Diagnostic Pack授权 |
| ASH Top 等待事件 | 11g+ | 只读 | v$active_session_history |
| DB Time / 负载画像 | 11g+ | 只读 | AWR Load Profile |
| SGA / PGA 使用与建议 | 11g+ | 只读 | v$sga, v$pga_target_advice |

#### 缓存与统计

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| Buffer Cache 命中率 | 11g+ | 只读 | v$sysstat |
| Library Cache / 共享池 | 11g+ | 只读 | v$librarycache |
| 表 / 索引统计信息是否过期 | 11g+ | 只读 | dba_tab_statistics |
| 收集统计信息（DBMS_STATS） | 11g+ | 谨慎 | 生产建议非高峰执行 |

#### 索引

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 未使用索引清单 | 11g+ | 只读 | v$object_usage，需先监控 |
| 缺失索引建议（SQL Tuning） | 11g+ | 只读 | DBMS_SQLTUNE |
| 索引碎片 / 重建评估 | 11g+ | 谨慎 | 重建前评估锁与空间 |

### 慢SQL

#### 定位慢SQL

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| Top SQL by Elapsed Time | 11g+ | 只读 | v$sql / AWR Top SQL |
| Top SQL by Buffer Gets | 11g+ | 只读 | 逻辑读最高 |
| Top SQL by Executions | 11g+ | 只读 | 执行次数最多 |
| 近1h 慢SQL（执行>5s） | 11g+ | 只读 | v$sql + elapsed |

#### 执行计划

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 查看执行计划（EXPLAIN PLAN） | 11g+ | 只读 | DBMS_XPLAN |
| 真实执行计划（DBMS_XPLAN.DISPLAY_CURSOR） | 11g+ | 只读 | 带A-Rows / Buffers |
| 全表扫描 SQL 清单 | 11g+ | 只读 | TABLE ACCESS FULL |
| 绑定变量窥探 / 直方图检查 | 11g+ | 只读 | v$sql_bind_capture |

#### 优化手段

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| SQL Profile / Baseline 建议 | 11g+ | 谨慎 | SQL Tuning Advisor |
| 自动索引建议（19c+） | 19c+ | 谨慎 | DBMS_AUTO_INDEX |
| Hint 改写模板 | 11g+ | 谨慎 | /*+ INDEX / PARALLEL */ 仅模板 |

### 锁 / 会话 / 等待

#### 锁与阻塞

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 当前阻塞锁链 | 11g+ | 只读 | v$lock + v$session blocking |
| 死锁历史（ORA-00060） | 11g+ | 只读 | alert log / trace |
| 行锁等待详情 | 11g+ | 只读 | v$session + row_wait |
| 杀会话（ALTER SYSTEM KILL） | 11g+ | 危险 | 先确认业务影响 |

#### 会话与等待

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 活跃会话 Top | 11g+ | 只读 | v$session status=ACTIVE |
| 等待事件 Top 10 | 11g+ | 只读 | v$system_event |
| 长运行会话（>30min） | 11g+ | 只读 | v$session + sql |

### 空间 / 存储

#### 表空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 表空间扩容（ADD DATAFILE） | 11g+ | 危险 | 先查磁盘余量 |
| 数据文件 / 自动扩展状态 | 11g+ | 只读 | dba_data_files |
| 段增长 Top 20 | 11g+ | 只读 | dba_segments |
| 大表 / 大索引清单 | 11g+ | 只读 | 按MB排序 |
| 回收站清理（PURGE） | 11g+ | 谨慎 | DROP 后恢复会失效 |

### 备份恢复

#### RMAN

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| RMAN 全量备份命令 | 11g+ | 谨慎 | BACKUP DATABASE PLUS ARCHIVELOG |
| RMAN 增量 0/1 级备份 | 11g+ | 谨慎 | Level 0/1 + 归档 |
| RMAN 备份集 / 保留策略检查 | 11g+ | 只读 | LIST BACKUP / REPORT |
| RMAN 恢复演练清单 | 11g+ | 谨慎 | 测试库演练，勿在生产直接跑 |

#### 闪回与 PITR

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 闪回查询（AS OF TIMESTAMP） | 11g+ | 只读 | 需UNDO保留 |
| 闪回表（FLASHBACK TABLE） | 11g+ | 危险 | 需行移动开启 |
| RMAN 表级 PITR | 12c+ | 危险 | 12c+支持，4-12h |
| 块损坏 BMR 恢复 | 11g+ | 危险 | BLOCKRECOVER |

### 高可用 / 容灾

#### RAC

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| RAC 节点 / 实例状态 | 11g+ | 只读 | srvctl / crsctl |
| RAC 互联 / 心跳检查 | 11g+ | 只读 | oifcfg / 集群日志 |
| 服务切换 / 负载均衡检查 | 11g+ | 只读 | srvctl config service |

#### DG / OGG

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| DG 备库延迟（Apply Lag） | 11g+ | 只读 | v$dataguard_stats |
| DG 切换演练（Switchover） | 11g+ | 危险 | 演练前停写确认 |
| OGG 抽取 / 投递延迟 | 11g+ | 只读 | INFO ALL / lag |
| 容灾 RPO=0 演练清单 | 11g+ | 谨慎 | 按你的银行案例沉淀 |

### 用户 / 权限 / 安全

#### 账号

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户 / 角色 / 权限清单 | 11g+ | 只读 | dba_users / dba_role_privs |
| 密码过期 / 锁定账号 | 11g+ | 只读 | dba_users account_status |
| 审计开启与审计日志 | 11g+ | 只读 | 11g审计 / 12c+统一审计 |

---

## MySQL（45 条）· 5.7 / 8.0 / 8.4 LTS

> 主力，MySQL 8.0 OCP，MGR/MHA/主从

### 日常巡检

#### 实例与状态

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例状态 / 版本 / uptime | 5.7+ | 只读 | SHOW GLOBAL STATUS |
| 连接数 / 最大连接 | 5.7+ | 只读 | Threads_connected |
| 慢查询开关与阈值 | 5.7+ | 只读 | slow_query_log |
| 错误日志近24h | 5.7+ | 只读 | error log |
| 定时任务 / EVENT 状态 | 5.7+ | 只读 | SHOW EVENTS |

#### 健康指标

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| InnoDB Buffer Pool 命中率 | 5.7+ | 只读 | Innodb_buffer_pool_read% |
| QPS / TPS 趋势 | 5.7+ | 只读 | Questions / Com_commit |
| 临时表 / 排序溢出 | 5.7+ | 只读 | Created_tmp_disk_tables |

### 性能优化

#### 参数与内存

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 关键参数速查（innodb_buffer_pool_size 等） | 5.7+ | 只读 | SHOW VARIABLES |
| Buffer Pool 建议值 | 5.7+ | 只读 | 按内存 70-80% 估算 |
| 统计信息 / 直方图（8.0+） | 8.0+ | 只读 | information_schema.COLUMN_STATISTICS |

#### 索引

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 未使用索引（sys.schema_unused_indexes） | 5.7+ | 只读 | sys 库 |
| 冗余 / 重复索引 | 5.7+ | 只读 | sys.schema_redundant_indexes |
| 索引基数与选择性 | 5.7+ | 只读 | SHOW INDEX |
| 不可见索引（8.0+） | 8.0+ | 谨慎 | Invisible Index 试索引 |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢查询日志分析（mysqldumpslow / pt-query-digest） | 5.7+ | 只读 | 命令行工具 |
| performance_schema Top SQL | 5.7+ | 只读 | events_statements_summary |
| sys.statements_with_runtimes_in_95th | 5.7+ | 只读 | sys 库 95分位 |
| 全表扫描 SQL | 5.7+ | 只读 | No_index_used |

#### 执行计划

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| EXPLAIN / EXPLAIN ANALYZE（8.0.18+） | 8.0+ | 只读 | 真实执行耗时 |
| 执行计划走索引 vs 全表 | 5.7+ | 只读 | type=ALL 警示 |
| JOIN 顺序 / 驱动表检查 | 5.7+ | 只读 | EXPLAIN rows |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 当前锁等待（sys.innodb_lock_waits） | 5.7+ | 只读 | sys 库 |
| 死锁日志（SHOW ENGINE INNODB STATUS） | 5.7+ | 只读 | LATEST DETECTED DEADLOCK |
| 杀会话（KILL CONNECTION） | 5.7+ | 危险 | 先确认 |
| 长事务（>30min） | 5.7+ | 只读 | information_schema.INNODB_TRX |

### 空间 / 存储

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 库 / 表大小 Top 20 | 5.7+ | 只读 | information_schema.TABLES |
| 碎片率与 OPTIMIZE 评估 | 5.7+ | 谨慎 | OPTIMIZE 会锁表（8.0 在线部分） |
| ibdata / undo / redo 大小 | 5.7+ | 只读 | SHOW VARIABLES |
| 磁盘使用率预警 | 5.7+ | 只读 | df + 表大小 |

### 备份恢复

#### 逻辑备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| mysqldump 全备 / 单库 / 单表 | 5.7+ | 谨慎 | --single-transaction |
| mydumper 并行备份 | 5.7+ | 谨慎 | 大库首选 |
| binlog PITR 恢复 | 5.7+ | 危险 | mysqlbinlog + STOPAT |

#### 物理备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| XtraBackup 全备 / 增量 | 5.7+ | 谨慎 | xtrabackup --backup |
| XtraBackup 恢复演练 | 5.7+ | 谨慎 | --prepare + --copy-back |
| 闪回（binlog2sql） | 5.7+ | 危险 | DELETE/UPDATE 闪回 |

### 高可用 / 复制

#### 主从

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 主从延迟（Seconds_Behind_Master） | 5.7+ | 只读 | SHOW SLAVE STATUS |
| 复制错误定位（Last_Error） | 5.7+ | 只读 | IO/SQL线程 |
| GTID 一致性检查 | 5.7+ | 只读 | gtid_executed |

#### MGR / MHA

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| MGR 成员状态 | 8.0+ | 只读 | performance_schema.replication_group_members |
| MGR 主节点切换 | 8.0+ | 危险 | group_replication_set_as_primary |
| MHA 切换演练清单 | 5.7+ | 谨慎 | masterha_check_status |

### 用户 / 安全

#### 账号

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户 / 权限清单 | 5.7+ | 只读 | mysql.user |
| 弱密码 / 无密码账号 | 5.7+ | 只读 | authentication_string 为空 |
| 审计（8.0 audit log / 5.7 插件） | 5.7+ | 只读 | 按版本区分 |

---

## PostgreSQL（26 条）· 12 / 13 / 14 / 15 / 16 / 17

> PCA 考证中，主力扩展方向

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 版本 / uptime / 连接数 | 12+ | 只读 | pg_stat_activity |
| WAL 生成量 | 12+ | 只读 | pg_stat_wal |
| 后台进程状态 | 12+ | 只读 | pg_stat_activity backend_type |

### 性能优化

#### 参数与缓存

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| shared_buffers / work_mem 建议 | 12+ | 只读 | SHOW |
| 缓存命中率（heap / index） | 12+ | 只读 | pg_statio_user_tables |
| 统计信息 / ANALYZE 状态 | 12+ | 只读 | pg_stat_user_tables |
| 自动 VACUUM 状态 | 12+ | 只读 | autovacuum |

#### 索引

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 未使用索引 | 12+ | 只读 | pg_stat_user_indexes idx_scan=0 |
| 缺失索引（hypopg 评估） | 12+ | 谨慎 | hypopg 扩展 |
| 膨胀索引 / bloat 评估 | 12+ | 只读 | pgstattuple |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| pg_stat_statements Top SQL | 12+ | 只读 | 需开启扩展 |
| 慢查询日志（log_min_duration） | 12+ | 只读 | postgresql.conf |
| EXPLAIN ANALYZE | 12+ | 只读 | 真实耗时+Buffers |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁链（pg_blocking_pids） | 12+ | 只读 | pg_stat_activity |
| 死锁统计 | 12+ | 只读 | pg_stat_database deadlocks |
| 终止会话（pg_terminate_backend） | 12+ | 危险 | 先确认 |

### 空间

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 库 / 表大小 Top | 12+ | 只读 | pg_database_size |
| 表膨胀 / VACUUM 建议 | 12+ | 谨慎 | VACUUM / VACUUM FULL 区分 |
| 死元组比例 | 12+ | 只读 | n_dead_tup |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| pg_dump / pg_dumpall | 12+ | 谨慎 | 逻辑备份 |
| pg_basebackup 物理备份 | 12+ | 谨慎 | 流复制备份 |
| PITR（WAL + recovery_target_time） | 12+ | 危险 | 需连续WAL |

### 高可用

#### 流复制

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 主从延迟（pg_stat_replication） | 12+ | 只读 | replay_lag |
| 同步 / 异步模式检查 | 12+ | 只读 | synchronous_standby_names |

### 用户 / 安全

#### 账号

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 角色 / 权限清单 | 12+ | 只读 | pg_roles |
| 行级安全（RLS）检查 | 12+ | 只读 | pg_policies |

---

## SQL Server（20 条）· 2016 / 2019 / 2022

> AlwaysOn 方向

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 版本 / 实例状态 | 2016+ | 只读 | @@VERSION / sys.dm_os_sys_info |
| 连接 / 作业（Agent Job）状态 | 2016+ | 只读 | msdb.dbo.sysjobs |

### 性能优化

#### DMV

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 缓存命中率 / 内存使用 | 2016+ | 只读 | sys.dm_os_performance_counters |
| 缺失索引 DMV | 2016+ | 只读 | sys.dm_db_missing_index_details |
| 统计信息过期 | 2016+ | 只读 | sys.stats |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| Query Store Top SQL（2016+） | 2016+ | 只读 | sys.query_store_runtime_stats |
| 最耗 CPU / IO 的查询 | 2016+ | 只读 | sys.dm_exec_query_stats |
| 执行计划（实际 vs 预估） | 2016+ | 只读 | SSMS / DMV |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞链（sys.dm_exec_requests） | 2016+ | 只读 | blocking_session_id |
| 死锁图（Extended Events） | 2016+ | 只读 | xml_deadlock_report |
| KILL 会话 | 2016+ | 危险 | KILL spid |

### 空间

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 数据库 / 文件大小 Top | 2016+ | 只读 | sys.database_files |
| 日志文件增长 / VLF | 2016+ | 只读 | DBCC LOGINFO |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 完整 / 差异 / 日志备份 | 2016+ | 谨慎 | BACKUP DATABASE/LOG |
| STOPAT 时间点恢复 | 2016+ | 危险 | RESTORE ... STOPAT |
| 备份历史检查 | 2016+ | 只读 | msdb.dbo.backupset |

### 高可用

#### AlwaysOn

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 可用性组状态 / 同步延迟 | 2016+ | 只读 | sys.dm_hadr_availability_replica_states |
| 故障转移演练清单 | 2016+ | 危险 | AG Failover |

### 用户 / 安全

#### 账号

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 登录名 / 用户 / 角色 | 2016+ | 只读 | sys.server_principals |
| 审计（SQL Audit） | 2016+ | 只读 | sys.server_audits |

---

## 达梦 DM8（16 条）· DM8 / DM8.1

> 国产化迁移方向，GCA/YCA 相关

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例状态 / 版本 | DM8+ | 只读 | SELECT * FROM V$INSTANCE |
| 表空间 / 数据文件 | DM8+ | 只读 | DBA_TABLESPACES |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 缓存命中率 / 内存 | DM8+ | 只读 | V$BUFFERPOOL |
| 统计信息收集 | DM8+ | 谨慎 | DBMS_STATS |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢SQL Top（V$SQL） | DM8+ | 只读 | V$SQL |
| 执行计划（EXPLAIN） | DM8+ | 只读 | DM EXPLAIN |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁 / 会话 | DM8+ | 只读 | V$LOCK / V$SESSIONS |
| 杀会话 | DM8+ | 危险 | SP_CLOSE_SESSION |

### 空间

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 表空间使用率 | DM8+ | 只读 | DBA_DATA_FILES |
| 大表 Top | DM8+ | 只读 | DBA_SEGMENTS |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 全备 / 增量（BACKUP DATABASE） | DM8+ | 谨慎 | DMRMAN |
| 闪回 / 时间点恢复 | DM8+ | 危险 | DMRMAN RESTORE |

### 高可用

#### DW / DSC

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 数据守护（DW）状态 | DM8+ | 只读 | V$DMWATCHER |
| DSC 集群状态 | DM8+ | 只读 | DMASM |

### 迁移

#### 迁移

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| Oracle → DM 迁移检查清单 | DM8+ | 谨慎 | DTS 工具 / 数据类型映射 |
| 兼容性检查（方言差异） | DM8+ | 只读 | NVL/ROWNUM 等 |

---

## OceanBase（16 条）· 3.x / 4.x（MySQL模式 / Oracle模式）

> OBCA 考证中，国产化方向

### 日常巡检

#### 集群

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 集群 / 租户 / Zone 状态 | 4.x | 只读 | __all_server / __all_tenant |
| 资源单元（Unit）使用 | 4.x | 只读 | __all_unit |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 租户内存 / CPU 使用 | 4.x | 只读 | GV$OB_MEMORY |
| 缓存 / 合并（Major Compaction）状态 | 4.x | 只读 | __all_zone / 合并进度 |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| Top SQL（GV$OB_SQL_AUDIT） | 4.x | 只读 | SQL Audit |
| 执行计划（EXPLAIN） | 4.x | 只读 | MySQL/Oracle模式区分 |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 活跃会话 / 阻塞 | 4.x | 只读 | GV$OB_PROCESSLIST |
| 杀会话（KILL） | 4.x | 危险 | KILL id |

### 空间

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 表 / 分区大小 | 4.x | 只读 | __all_table |
| 磁盘使用 / 数据压缩 | 4.x | 只读 | __all_virtual_disk_stat |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 物理备份 / 归档（OB 备份） | 4.x | 谨慎 | BACKUP DATABASE |
| 闪回 / 时间点恢复 | 4.x | 危险 | FLASHBACK / PITR |

### 高可用

#### 高可用

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 多副本 / Paxos 状态 | 4.x | 只读 | __all_ls |
| 主备切换演练 | 4.x | 危险 | 切换前确认 |

### 迁移

#### 迁移

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| MySQL → OB 迁移清单 | 4.x | 谨慎 | OMS 工具 |
| Oracle → OB 迁移清单 | 4.x | 谨慎 | OMS / 数据类型映射 |

---

## GBase 8a / 8s（9 条）· 8a MPP / 8s OLTP

> GBase GCA，国产化方向

### 日常巡检

#### 集群

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 集群节点状态（8a） | 8a | 只读 | gcadmin |
| 实例状态（8s） | 8s | 只读 | onstat |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 分布键 / 数据倾斜检查（8a） | 8a | 只读 | 数据分布 |
| 统计信息 / 优化器 | 8a | 只读 | ANALYZE |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢SQL Top | 8a/8s | 只读 | 系统表 / 日志 |
| 执行计划 | 8a/8s | 只读 | EXPLAIN |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 8a 备份（gcbackup） | 8a | 谨慎 | 集群备份 |
| 8s 逻辑备份（dbexport） | 8s | 谨慎 | dbexport |

### 迁移

#### 迁移

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| Oracle/MySQL → GBase 迁移清单 | 8a/8s | 谨慎 | 迁移工具 / 类型映射 |

---

## TiDB（10 条）· 6.x / 7.x / 8.x

> MySQL 兼容分布式，扩展方向

### 日常巡检

#### 集群

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 集群状态（tiup cluster display） | 6.x+ | 只读 | tiup |
| TiKV / PD 状态 | 6.x+ | 只读 | pd-ctl / Grafana |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 热点 Region 检查 | 6.x+ | 只读 | INFORMATION_SCHEMA.TIKV_REGION_STATUS |
| 统计信息 / ANALYZE | 6.x+ | 谨慎 | ANALYZE TABLE |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢查询日志 / Top SQL（Dashboard） | 6.x+ | 只读 | INFORMATION_SCHEMA.SLOW_QUERY |
| EXPLAIN ANALYZE | 6.x+ | 只读 | TiDB 执行计划 |

### 高可用

#### 高可用

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 多副本 / Raft 状态 | 6.x+ | 只读 | PD |
| TiFlash 同步延迟 | 6.x+ | 只读 | TiFlash 副本 |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| BR 全备 / PITR | 6.x+ | 谨慎 | br backup / restore |
| Dumpling 逻辑备份 | 6.x+ | 谨慎 | dumpling |

---

## 通用 / 跨库工具（11 条）· 全库通用

> 不连库的本地工具，uTools 插件 v0.1 已有部分

### SQL 工具

#### 通用

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| SQL 格式化（Oracle/MySQL/PG/SQL Server） | 全版本 | 只读 | v0.1 已做 |
| 方言互转 Oracle↔MySQL | 全版本 | 谨慎 | v0.1 已做，规则式 |
| SQL 脱敏 | 全版本 | 只读 | v0.1 已做 |
| 列表转 IN / 批量 INSERT | 全版本 | 只读 | v0.1 已做 |
| 时间戳互转 | 全版本 | 只读 | v0.1 已做 |

### 连接与检查

#### 通用

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 连接串速查（JDBC / ODBC） | 全版本 | 只读 | 各库连接串模板 |
| 端口 / 连通性检查 | 全版本 | 只读 | telnet / nc 模板 |
| 字符集 / 时区检查 | 全版本 | 只读 | 各库字符集查询 |

### NoSQL（第二期）

#### Redis / Mongo

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| Redis 常用命令（INFO / SLOWLOG / 内存） | 6.x/7.x | 只读 | 二期 |
| MongoDB 慢查询 / 索引 | 6.x/7.x | 只读 | 二期 |
| SQLite 常用命令 | 3.x | 只读 | 二期 |

---

## v0.3 新增（112 条）· 墨天轮 2026-11 榜单国产库

来源：https://www.modb.pro/dbRank（2026 年 11 月，136 个数据库参与）。第一批只补关系型 Top 15 里缺的 8 个库，每库 14 条；平凯数据库（第 6 名）经核实是 TiDB 商业版，不重复建库，改补第 10 名 TDengine。脚本均从各库官方手册提取，未在真实环境跑过的条目 notes 里标“需实测核对”。

## 金仓 KingBaseES（14 条）· KES V9 / V8.6

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例状态 / 版本 | V9+ | 只读 | version(), sys_stat_activity |
| 无效对象清单 | V9+ | 只读 | DBA_OBJECTS（Oracle 兼容模式） |

### 性能优化

#### 参数与缓存

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 缓存命中率 / 内存 | V9+ | 只读 | sys_stat_database |
| 统计信息收集 | V9+ | 谨慎 | ANALYZE |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢SQL Top（sys_stat_statements） | V9+ | 只读 | sys_stat_statements |
| 执行计划（EXPLAIN ANALYZE） | V9+ | 只读 | EXPLAIN ANALYZE |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁 / 会话 | V9+ | 只读 | sys_locks / sys_stat_activity |
| 杀会话 | V9+ | 危险 | pg_terminate_backend |

### 空间

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 表空间大小一览 | V9+ | 只读 | sys_tablespace / sys_tablespace_size |
| 大表 Top | V9+ | 只读 | sys_total_relation_size |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 物理备份（sys_rman 全量 / 增量） | V9+ | 谨慎 | sys_rman |
| 时间点恢复演练清单 | V9+ | 危险 | sys_rman restore / PITR |

### 高可用

#### 流复制

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 主备 / 流复制状态 | V9+ | 只读 | sys_stat_replication |

### 用户 / 安全

#### 账号

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户与角色列表 | V9+ | 只读 | pg_roles |

## PolarDB（14 条）· MySQL 5.7 / 8.0；PostgreSQL 11/14/15/16/17

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例版本 / 引擎版本 | MySQL 5.7 / 8.0 | 只读 | SELECT VERSION() |
| 无主键表巡检 | MySQL 5.7 / 8.0 | 只读 | information_schema.TABLES / TABLE_CONSTRAINTS |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| InnoDB Buffer Pool 命中率 | MySQL 8.0 | 只读 | SHOW GLOBAL STATUS Innodb_buffer_pool_read% |
| 统计信息收集（ANALYZE TABLE） | MySQL 8.0 | 谨慎 | ANALYZE TABLE |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢SQL Top（PolarDB 专属 sql_sharing） | MySQL 8.0.1 修订版 8.0.1.1.30+ / 8.0.2 修订版 8.0.2.2.12+ | 只读 | information_schema.sql_sharing |
| 执行计划（EXPLAIN） | MySQL 8.0 | 只读 | EXPLAIN |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁 / 长事务 | MySQL 8.0 | 只读 | performance_schema.data_lock_waits / INNODB_TRX |
| 杀会话（KILL） | MySQL 5.7 / 8.0 | 危险 | KILL |

### 空间 / 存储

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 大表 Top | MySQL 5.7 / 8.0 | 只读 | information_schema.TABLES |
| 库级存储用量 | MySQL 5.7 / 8.0 | 只读 | information_schema.TABLES 按库汇总 |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 备份 / Binlog 状态 | MySQL 5.7 / 8.0 | 只读 | SHOW BINARY LOGS |
| PITR 恢复演练清单 | MySQL 5.7 / 8.0 | 危险 | 控制台按时间点恢复 |

### 高可用 / 复制

#### 复制

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 主备 / 只读节点状态 | MySQL 5.7 / 8.0 | 只读 | read_only / PROCESSLIST |

### 用户 / 安全

#### 用户

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户列表与权限 | MySQL 5.7 / 8.0 | 只读 | mysql.user / SHOW GRANTS |

## GoldenDB（14 条）· GoldenDB V6 分布式/集中式/混合部署

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例版本 / 运行状态 | GoldenDB V6 分布式/集中式 | 只读 | VERSION() / SHOW GLOBAL STATUS |
| 分片表定义检查 | GoldenDB V6 分布式 | 只读 | SHOW CREATE TABLE |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| InnoDB 缓冲池命中率 | GoldenDB V6 分布式/集中式 | 只读 | performance_schema.global_status |
| 统计信息收集（ANALYZE TABLE） | GoldenDB V6 分布式/集中式 | 谨慎 | ANALYZE TABLE |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢SQL Top（performance_schema 摘要） | GoldenDB V6 分布式/集中式 | 只读 | events_statements_summary_by_digest |
| 执行计划（EXPLAIN） | GoldenDB V6 分布式/集中式 | 只读 | EXPLAIN |

### 锁/会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁 / 长事务 | GoldenDB V6 分布式/集中式 | 只读 | information_schema.innodb_trx |
| 杀会话（KILL） | GoldenDB V6 分布式/集中式 | 危险 | KILL |

### 空间/存储

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 库空间使用率 | GoldenDB V6 分布式/集中式 | 只读 | information_schema.TABLES |
| 分片数据分布 / 倾斜检查 | GoldenDB V6 分布式 | 只读 | 分片键 GROUP BY 计数 |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 备份 / Binlog 状态检查 | GoldenDB V6 分布式/集中式 | 只读 | SHOW BINARY LOGS / SHOW MASTER STATUS |
| 时间点恢复演练清单 | GoldenDB V6 分布式/集中式 | 危险 | OMM/Insight 恢复（无 SQL） |

### 高可用/容灾

#### 容灾

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 分片组主备复制状态 | GoldenDB V6 分布式 | 只读 | SHOW REPLICA STATUS / SHOW SLAVE STATUS |

### 用户/安全

#### 安全

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户列表 / 权限 | GoldenDB V6 分布式/集中式 | 只读 | mysql.user / SHOW GRANTS |

## TDSQL（14 条）· TDSQL MySQL版 5.7/8.0 分布式；TDSQL PostgreSQL版 分布式/集中式

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例版本 / 运行状态 | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | VERSION() / SHOW GLOBAL STATUS |
| 分片分布 / 倾斜检查 | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | 分片键 GROUP BY 计数 |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| InnoDB 缓冲池命中率 | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | performance_schema.global_status |
| 统计信息收集（ANALYZE TABLE） | TDSQL MySQL版 5.7/8.0 分布式 | 谨慎 | ANALYZE TABLE |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢SQL Top（performance_schema 摘要） | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | events_statements_summary_by_digest |
| 慢SQL Top（PG版 pg_stat_statements） | TDSQL PostgreSQL版 分布式/集中式 | 只读 | pg_stat_statements |

### 锁/会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁 / 长事务 | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | information_schema.innodb_trx |
| 杀会话（KILL） | TDSQL MySQL版 5.7/8.0 分布式 | 危险 | KILL |

### 空间/存储

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 库空间使用率 | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | information_schema.TABLES |
| 大表 Top | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | information_schema.TABLES |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 备份 / Binlog 状态检查 | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | SHOW BINARY LOGS / SHOW MASTER STATUS |
| 时间点恢复 / 回档演练清单 | TDSQL MySQL版 5.7/8.0 分布式；PG版 | 危险 | 控制台回档（无 SQL） |

### 高可用/容灾

#### 容灾

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 主备复制延迟 | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | SHOW REPLICA STATUS / SHOW SLAVE STATUS |

### 用户/安全

#### 安全

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户列表 / 权限 | TDSQL MySQL版 5.7/8.0 分布式 | 只读 | mysql.user / SHOW GRANTS |

## GaussDB（14 条）· 集中式 / 分布式 V2.0-8.x

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例版本 | 集中式 / 分布式 V2.0-8.x | 只读 | SELECT version() |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 会话内存 Top | 集中式 / 分布式 V2.0-8.x | 只读 | pv_session_memory_detail() |
| 统计信息收集（ANALYZE） | 集中式 / 分布式 V2.0-8.x | 谨慎 | ANALYZE / pg_stat_user_tables |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 归一化 SQL Top（dbe_perf.statement） | 集中式 V2.0-8.x（dbe_perf.statement）；分布式用 PGXC_SQL_COUNT | 只读 | dbe_perf.statement / SUMMARY_STATEMENT |
| 执行计划（EXPLAIN） | 集中式 / 分布式 V2.0-8.x | 只读 | EXPLAIN |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁 / 等锁线程 | 集中式 / 分布式 V2.0-8.x | 只读 | pg_locks / pg_thread_wait_status |
| 杀会话（pg_terminate_backend） | 集中式 / 分布式 V2.0-8.x | 危险 | pg_terminate_backend |

### 空间 / 存储

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 表空间使用率 | 集中式 / 分布式 V2.0-8.x | 只读 | pg_tablespace / pg_tablespace_size |
| 大表 Top | 集中式 / 分布式 V2.0-8.x | 只读 | pg_table_size / pg_tables |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 物理备份（gs_backup） | 集中式 / 分布式（自建 openGauss 内核）；云上 GaussDB 以控制台备份为准 | 谨慎 | gs_backup |
| PITR 恢复演练清单 | 集中式 / 分布式 V2.0-2.1+ | 危险 | 控制台恢复到指定时间点 |

### 高可用 / 复制

#### 复制

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 主备同步状态 | 集中式 / 分布式 V2.0-8.x | 只读 | pg_stat_replication |
| 分布式节点列表（pgxc_node） | 分布式 V2.0-8.x（集中式无此视图） | 只读 | pgxc_node |

### 用户 / 安全

#### 用户

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户列表（gs_user） | 集中式 / 分布式 V2.0-8.x | 只读 | gs_user |

## TDengine（14 条）· 3.x（社区版 / 企业版）

### 日常巡检

#### 集群

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 版本与数据节点状态 | 3.x | 只读 | SELECT SERVER_VERSION() / SHOW DNODES |
| 库 / 超级表清单 | 3.x | 只读 | SHOW DATABASES / SHOW STABLES |

### 性能/写入

#### 查询

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 正在执行的查询 | 3.4+ | 只读 | SHOW QUERIES |
| 超级表下采样聚合（INTERVAL） | 3.x | 只读 | INTERVAL / PARTITION BY tbname |

### 慢查询

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢查询定位（SHOW QUERIES + EXPLAIN） | 3.x | 只读 | SHOW QUERIES / EXPLAIN |
| 最新数据到达检查（LAST_ROW） | 3.x | 只读 | LAST_ROW |

### 空间/压缩

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 库空间与压缩率 | 3.x | 只读 | information_schema.ins_databases |
| 虚拟组与子表分布 | 3.x | 只读 | SHOW VGROUPS / SHOW TABLES |

### 保留策略

#### 保留

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 库保留参数查看 | 3.x | 只读 | SHOW CREATE DATABASE |
| 修改保留时长与压缩 | 3.x | 谨慎 | ALTER DATABASE KEEP / COMP |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 逻辑备份（taosdump） | 3.x | 谨慎 | taosdump |
| 企业版全备与恢复 | 3.x 企业版 | 危险 | CREATE FULL BACKUP / taosd --restore |

### 高可用

#### 集群

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 节点与副本状态 | 3.x | 只读 | SHOW DNODES / SHOW MNODES / SHOW VGROUPS |

### 用户/安全

#### 用户

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户与授权 | 3.x | 谨慎 | SHOW USERS / CREATE USER |

## 崖山 YashanDB（14 条）· YashanDB 23.2

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 实例状态 / 版本 | 23.2+ | 只读 | V$INSTANCE, V$VERSION |
| 无效对象清单 | 23.2+ | 只读 | DBA_OBJECTS |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 缓存命中率 / 内存 | 23.2+ | 只读 | V$SYSSTAT |
| 统计信息收集 | 23.2+ | 谨慎 | DBMS_STATS |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢SQL Top（V$SQL） | 23.2+ | 只读 | V$SQL |
| 执行计划（EXPLAIN PLAN） | 23.2+ | 只读 | EXPLAIN PLAN / DBMS_XPLAN |

### 锁 / 会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁 / 会话 | 23.2+ | 只读 | V$LOCKED_OBJECT / V$SESSION |
| 杀会话 | 23.2+ | 危险 | ALTER SYSTEM KILL SESSION |

### 空间

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 表空间使用率 | 23.2+ | 只读 | DBA_DATA_FILES / DBA_FREE_SPACE |
| 大表 Top | 23.2+ | 只读 | DBA_SEGMENTS |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 备份 / 归档状态 | 23.2+ | 只读 | V$DATABASE / V$ARCHIVED_LOG |
| 时间点恢复演练清单 | 23.2+ | 危险 | PITR 演练 |

### 高可用

#### 主备

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 主备状态 / 复制延迟 | 23.2+ | 只读 | V$DATABASE / V$ARCHIVE_DEST_STATUS |

### 用户 / 安全

#### 账号

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户列表与权限 | 23.2+ | 只读 | DBA_USERS / DBA_SYS_PRIVS |

## openGauss（14 条）· 5.0 / 6.0 LTS

### 日常巡检

#### 实例

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 版本 / 集群状态（gs_om） | 5.0 / 6.0 LTS | 只读 | SELECT version() / gs_om -t status |
| 库大小与当前连接数 | 5.0 / 6.0 LTS | 只读 | pg_database_size / pg_stat_activity |

### 性能优化

#### 性能

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 大表 / 大索引 Top | 5.0 / 6.0 LTS | 只读 | pg_total_relation_size |
| 统计信息收集（ANALYZE） | 5.0 / 6.0 LTS | 谨慎 | ANALYZE |

### 慢SQL

#### 定位

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 慢SQL Top（GS_WLM_SESSION_INFO） | 5.0 / 6.0 LTS | 只读 | GS_WLM_SESSION_INFO |
| 执行计划（EXPLAIN） | 5.0 / 6.0 LTS | 只读 | EXPLAIN |

### 锁/会话

#### 锁

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 阻塞锁 / 等待会话 | 5.0 / 6.0 LTS | 只读 | pg_locks / pg_stat_activity |
| 强制终止会话 | 5.0 / 6.0 LTS | 危险 | pg_terminate_backend |

### 空间/存储

#### 空间

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 表空间使用情况 | 5.0 / 6.0 LTS | 只读 | pg_tablespace_size |
| 死元组 / 膨胀检查 | 5.0 / 6.0 LTS | 只读 | pg_stat_user_tables |

### 备份恢复

#### 备份

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 逻辑备份（gs_dump） | 5.0 / 6.0 LTS | 谨慎 | gs_dump |
| 物理备份与恢复（gs_probackup） | 5.0 / 6.0 LTS | 危险 | gs_probackup |

### 高可用/容灾

#### 主备

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 主备复制状态与延迟 | 5.0 / 6.0 LTS | 只读 | pg_stat_replication / gs_om |

### 用户/安全

#### 用户

| 脚本 / 命令 | 适用版本 | 风险 | 说明 |
|---|---|---|---|
| 用户与权限 | 5.0 / 6.0 LTS | 谨慎 | pg_roles / CREATE USER |
