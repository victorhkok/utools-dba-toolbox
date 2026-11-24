-- 同步 / 异步模式检查
-- 适用版本：12+
-- 风险：只读
-- 说明：synchronous_standby_names。synchronous_standby_names 为空即异步；同步模式下主库提交要等备库确认。
-- 大类：高可用 / 小类：流复制

SHOW synchronous_standby_names;
SHOW synchronous_commit;
SELECT application_name, sync_state, state
FROM pg_stat_replication
ORDER BY application_name
LIMIT 20;
