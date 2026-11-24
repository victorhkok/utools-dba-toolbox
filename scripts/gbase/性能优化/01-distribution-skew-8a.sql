-- 分布键 / 数据倾斜检查（8a）
-- 适用版本：8a
-- 风险：只读
-- 说明：数据分布
-- 备注：8a 分布信息系统表名需在 8a 实测核对，本条只给通用表大小查询。

SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema') ORDER BY TABLE_ROWS DESC LIMIT 20;
-- 分布键与倾斜详情以 8a 的分布信息表为准，系统表名按版本不同，需在 8a 实测核对，不要硬编。
