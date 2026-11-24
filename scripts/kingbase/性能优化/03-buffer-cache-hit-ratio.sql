SELECT datname, blks_hit, blks_read,
  ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS hit_ratio_pct
FROM sys_stat_database
ORDER BY datname;
