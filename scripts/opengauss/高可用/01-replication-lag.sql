-- 主库视角：备库同步状态与日志位置（官方手册列名已核对）：
SELECT application_name, client_addr, state, sync_state, sync_priority,
  sender_sent_location, receiver_write_location, receiver_flush_location, receiver_replay_location
FROM pg_stat_replication;
-- shell: gs_om -t status
