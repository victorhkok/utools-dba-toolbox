SELECT trx_id, trx_state, trx_started, trx_mysql_thread_id, trx_query, trx_rows_locked
FROM information_schema.innodb_trx
ORDER BY trx_started
LIMIT 20;
