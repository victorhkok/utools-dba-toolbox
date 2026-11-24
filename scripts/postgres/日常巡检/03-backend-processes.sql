-- 后台进程状态
-- 适用版本：12+
-- 风险：只读
-- 说明：pg_stat_activity backend_type。backend_type 区分 autovacuum / walsender / checkpointer 等后台进程。
-- 大类：日常巡检 / 小类：实例

SELECT backend_type, state, count(*) AS cnt
FROM pg_stat_activity
GROUP BY backend_type, state
ORDER BY cnt DESC
LIMIT 20;
SELECT pid, backend_type, state, now() - query_start AS duration, left(query, 200) AS query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start
LIMIT 20;
