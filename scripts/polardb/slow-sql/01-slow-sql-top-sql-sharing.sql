SELECT * FROM information_schema.sql_sharing
WHERE TYPE = 'sql'
ORDER BY SUM_EXEC_TIME DESC
LIMIT 10;
