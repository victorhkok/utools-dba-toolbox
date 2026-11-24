SELECT datname, pg_size_pretty(pg_database_size(datname)) AS size,
  (SELECT count(*) FROM pg_stat_activity a WHERE a.datid = d.oid) AS connections
FROM pg_database d ORDER BY pg_database_size(datname) DESC;
