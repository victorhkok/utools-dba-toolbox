SELECT application_name, client_addr, state, sync_state,
  sent_lsn, write_lsn, flush_lsn, replay_lsn
FROM sys_stat_replication;
-- 备库延迟（在备库执行）：
-- SELECT now() - pg_last_xact_replay_timestamp() AS replay_delay;
