-- DG 备库延迟（Apply Lag）
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$dataguard_stats
-- 提醒：apply lag 和 transport lag 是两个值，v$dataguard_stats 里分开列；备库查要在备库上执行，主库查不到备库延迟。

SELECT name, value, time_computed, datum_time
FROM   v$dataguard_stats;

SELECT database_role, protection_mode, switchover_status, open_mode
FROM   v$database;
