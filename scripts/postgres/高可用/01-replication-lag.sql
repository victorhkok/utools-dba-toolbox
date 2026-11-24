-- 主从延迟（pg_stat_replication）
-- 适用版本：12+
-- 风险：只读
-- 说明：replay_lag。replay_lag 是备库回放延迟，write/flush 延迟大而 replay 小时说明回放跟不上。
-- 大类：高可用 / 小类：流复制

SELECT application_name, client_addr, state, sync_state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag_bytes,
       replay_lag, write_lag, flush_lag
FROM pg_stat_replication
ORDER BY replay_lag DESC
LIMIT 20;
