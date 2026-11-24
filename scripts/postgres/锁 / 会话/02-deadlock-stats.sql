-- 死锁统计
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_stat_database deadlocks。pg_stat_database 只有死锁次数，没有死锁明细，明细要去日志里找 deadlock detected。
-- 大类：锁 / 会话 / 小类：锁

SELECT datname, deadlocks, stats_reset
FROM pg_stat_database
ORDER BY deadlocks DESC
LIMIT 20;
