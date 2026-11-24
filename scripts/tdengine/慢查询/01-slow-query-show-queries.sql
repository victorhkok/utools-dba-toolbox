-- 1. 先看当前在跑的查询（只读）：
SHOW QUERIES;
-- 2. 对可疑 SQL 看执行计划（模板，替换为真实 SQL）：
EXPLAIN SELECT * FROM <STABLE> WHERE ts >= now - 1h;
