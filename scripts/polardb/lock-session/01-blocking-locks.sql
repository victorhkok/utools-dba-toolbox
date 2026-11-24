SELECT R.trx_id AS waiting_trx_id, R.trx_query AS waiting_query,
  B.trx_id AS blocking_trx_id, B.trx_query AS blocking_query,
  R.trx_started AS waiting_since
FROM performance_schema.data_lock_waits W
JOIN information_schema.INNODB_TRX B ON B.trx_id = W.blocking_engine_transaction_id
JOIN information_schema.INNODB_TRX R ON R.trx_id = W.requesting_engine_transaction_id;
