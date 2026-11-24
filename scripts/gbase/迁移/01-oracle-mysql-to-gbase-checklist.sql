-- Oracle/MySQL → GBase 迁移清单
-- 适用版本：8a/8s
-- 风险：谨慎
-- 说明：迁移工具 / 类型映射
-- 备注：迁移工具与类型映射需按 8a/8s 版本核对，分布键选择是 8a 迁移的关键。

-- 迁移前检查（只读，通用）：
SELECT TABLE_SCHEMA, COUNT(*) AS TABLE_CNT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema','mysql','sys') GROUP BY TABLE_SCHEMA ORDER BY TABLE_CNT DESC LIMIT 20;
-- 数据类型映射、分布键选择、字符集需以 GBase 迁移工具评估报告为准。
