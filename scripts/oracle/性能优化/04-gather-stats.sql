-- 收集统计信息（DBMS_STATS）
-- 适用版本：11g+
-- 风险：谨慎
-- 说明：生产建议非高峰执行
-- 提醒：生产高峰不要全库收集；cascade=>TRUE 会连索引一起收集，degree 按 CPU 核数填，勿填过大。

-- 先查（只读确认）：
SELECT owner, table_name, last_analyzed, stale_stats
FROM   dba_tab_statistics
WHERE  owner = '<schema>'
  AND  table_name = '<table_name>';

-- 再执行（谨慎：建议非高峰、测试库先跑）：
-- EXEC DBMS_STATS.gather_table_stats(ownname => '<schema>', tabname => '<table_name>', estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE, cascade => TRUE, degree => 4);
-- 整库模式：
-- EXEC DBMS_STATS.gather_schema_stats(ownname => '<schema>', estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE, cascade => TRUE, degree => 4);
