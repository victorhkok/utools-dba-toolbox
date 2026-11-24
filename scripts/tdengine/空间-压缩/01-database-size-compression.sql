SELECT db_name, data_size, storage_size,
  round(data_size * 1.0 / NULLIF(storage_size, 0), 2) AS compression_ratio
FROM information_schema.ins_databases ORDER BY storage_size DESC;
