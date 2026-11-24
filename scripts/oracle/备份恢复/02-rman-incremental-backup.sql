-- RMAN 增量 0/1 级备份
-- 适用版本：11g+
-- 风险：谨慎
-- 说明：Level 0/1 + 归档
-- 提醒：0 级是 1 级的基准，1 级恢复要依赖最近的 0 级；先做 0 级再做 1 级，不要只跑 1 级。

-- 0 级（全量基准，含归档）：
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
-- }
