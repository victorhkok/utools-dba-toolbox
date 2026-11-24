-- EXPLAIN ANALYZE
-- 适用版本：12+
-- 风险：只读
-- 说明：真实耗时+Buffers。EXPLAIN ANALYZE 会真实执行，大查询/写操作先在测试库跑，别在生产直接跑。
-- 大类：慢SQL / 小类：定位

-- 把 <query_text> 换成要分析的 SQL；真实执行，会跑完查询
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <query_text>;
