-- 8a 备份（gcbackup）
-- 适用版本：8a
-- 风险：谨慎
-- 说明：集群备份
-- 备注：gcbackup 参数需在 8a 实测核对，备份前确认磁盘余量与集群状态。

-- shell: gcbackup（GBase 8a 集群备份，需在协调节点执行）
-- shell: gcbackup -h
-- shell: gcbackup <备份目录>
