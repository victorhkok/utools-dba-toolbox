-- 数据守护（DW）状态
-- 适用版本：DM8+
-- 风险：只读
-- 说明：V$DMWATCHER
-- 备注：V$DMWATCHER 的列名与返回值需在 DM8 实测核对，未部署数据守护时该视图可能无数据。

SELECT TOP 20 * FROM V$DMWATCHER;
