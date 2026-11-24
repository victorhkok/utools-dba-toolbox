SELECT _wstart AS window_start, tbname, count(*) AS rows_cnt, avg(<MEASURE_COL>) AS avg_val
FROM <STABLE>
WHERE ts >= now - 1h AND ts < now
PARTITION BY tbname INTERVAL(5m)
ORDER BY window_start DESC, tbname LIMIT 100;
