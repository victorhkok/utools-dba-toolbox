-- EXPLAIN / EXPLAIN ANALYZE（8.0.18+）
-- 适用版本：8.0+
-- 风险：只读
-- 说明：真实执行耗时
-- 大类：慢SQL / 小类：执行计划
-- 8.0.18+ 才有 EXPLAIN ANALYZE；5.7/8.0.17 及以下只能用 EXPLAIN。
-- EXPLAIN ANALYZE 会真实执行 SQL，只对 SELECT 用，不要对 UPDATE/DELETE 用。
EXPLAIN <SELECT 语句>;
-- EXPLAIN ANALYZE <SELECT 语句>;
