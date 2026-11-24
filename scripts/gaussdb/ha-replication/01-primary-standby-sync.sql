SELECT application_name, client_addr, state, sync_state,
  sender_sent_location, receiver_write_location,
  receiver_flush_location, receiver_replay_location
FROM pg_stat_replication;
