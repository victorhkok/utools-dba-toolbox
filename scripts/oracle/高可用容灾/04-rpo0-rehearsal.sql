-- 容灾 RPO=0 演练清单
-- 适用版本：11g+
-- 风险：谨慎
-- 说明：按你的银行案例沉淀
-- 提醒：把握一般：本条是演练清单，RPO=0 依赖同步模式（MAXIMUM PROTECTION/AVAILABILITY）+网络，清单本身不保证 RPO=0，演练前先核对保护模式。

-- 演练前只读检查：
SELECT database_role, protection_mode, switchover_status FROM v$database;
SELECT name, value FROM v$dataguard_stats;
-- LIST BACKUP SUMMARY;  -- RMAN，确认最近全备
-- 演练清单（只在演练环境执行）：
-- 1. 确认 DG apply lag = 0、归档无缺口（v$archived_log gap 检查）
-- 2. 确认 RMAN 最近全备+归档可恢复（VALIDATE DATABASE）
-- 3. 按演练手册做 Switchover / Failover，记录切换耗时
-- 4. 切回后确认主备角色、应用连接、数据一致性抽查
