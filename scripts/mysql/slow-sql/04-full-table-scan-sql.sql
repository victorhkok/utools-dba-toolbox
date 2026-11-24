-- 全表扫描 SQL
-- 适用版本：5.7+
-- 风险：只读
-- 说明：No_index_used
-- 大类：慢SQL / 小类：定位
SELECT DIGEST_TEXT, COUNT_STAR, SUM_NO_INDEX_USED, SUM_NO_GOOD_INDEX_USED FROM performance_schema.events_statements_summary_by_digest WHERE SUM_NO_INDEX_USED > 0 ORDER BY SUM_NO_INDEX_USED DESC LIMIT 20;
SELECT * FROM sys.statements_with_full_table_scans LIMIT 20;
