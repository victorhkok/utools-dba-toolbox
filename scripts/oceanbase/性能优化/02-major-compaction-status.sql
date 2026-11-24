-- 缓存 / 合并（Major Compaction）状态
-- 适用版本：4.x
-- 风险：只读
-- 说明：__all_zone / 合并进度
-- 备注：合并进度视图名在 OB 3.x/4.x 间有变化，需在 OB 4.x 实测核对。

SELECT ZONE, STATUS, START_TIME FROM oceanbase.__all_zone LIMIT 20;
-- 合并进度以 OCP / obdiag 或 __all_virtual_merge_info 为准，视图名按版本不同：
-- 需在 OB 4.x 实测核对合并进度视图名后再查，不要硬编列名。
