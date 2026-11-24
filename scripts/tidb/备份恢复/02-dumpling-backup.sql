-- Dumpling 逻辑备份
-- 适用版本：6.x+
-- 风险：谨慎
-- 说明：dumpling
-- 备注：dumpling 参数需在 TiDB 6.x+ 实测核对，大库优先用 BR 物理备份。

-- shell: dumpling（TiDB 逻辑导出工具）
-- shell: dumpling -u root -P 4000 -h <TIDB_IP> -o /tmp/dumpling_out --filetype sql
