-- sys.statements_with_runtimes_in_95th
-- 适用版本：5.7+
-- 风险：只读
-- 说明：sys 库 95分位
-- 大类：慢SQL / 小类：定位
SELECT * FROM sys.statements_with_runtimes_in_95th LIMIT 20;
