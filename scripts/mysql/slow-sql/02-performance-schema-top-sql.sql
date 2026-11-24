-- performance_schema Top SQL
-- 适用版本：5.7+
-- 风险：只读
-- 说明：events_statements_summary
-- 大类：慢SQL / 小类：定位
-- 需 performance_schema 开启（默认开），否则结果为空。
SELECT DIGEST_TEXT, COUNT_STAR, ROUND(SUM_TIMER_WAIT / 1000000000000, 2) AS sum_sec, ROUND(AVG_TIMER_WAIT / 1000000000000, 4) AS avg_sec, SUM_ROWS_EXAMINED, SUM_ROWS_SENT FROM performance_schema.events_statements_summary_by_digest ORDER BY SUM_TIMER_WAIT DESC LIMIT 20;
