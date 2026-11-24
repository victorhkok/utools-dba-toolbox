-- 磁盘使用 / 数据压缩
-- 适用版本：4.x
-- 风险：只读
-- 说明：__all_virtual_disk_stat
-- 备注：__all_virtual_disk_stat 的列名需在 OB 4.x 实测核对，如无该视图请改用 OCP 磁盘监控。

SELECT SVR_IP, TOTAL_SIZE/1024/1024/1024 AS TOTAL_GB, USED_SIZE/1024/1024/1024 AS USED_GB
FROM oceanbase.__all_virtual_disk_stat LIMIT 20;
