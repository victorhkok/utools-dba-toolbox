SELECT NAME, VALUE FROM V$SYSSTAT
WHERE NAME LIKE '%physical reads%' OR NAME LIKE '%consistent gets%' OR NAME LIKE '%db block gets%';
-- 命中率估算：1 - physical reads / (consistent gets + db block gets)，分母为 0 时结果为 NULL。
