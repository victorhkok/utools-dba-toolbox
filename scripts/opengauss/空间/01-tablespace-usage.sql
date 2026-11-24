SELECT spcname, pg_size_pretty(pg_tablespace_size(spcname)) AS size,
  pg_tablespace_location(oid) AS location
FROM pg_tablespace ORDER BY pg_tablespace_size(spcname) DESC;
