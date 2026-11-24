-- 统计信息收集
-- 适用版本：DM8+
-- 风险：谨慎
-- 说明：DBMS_STATS
-- 备注：DM8 的 DBMS_STATS 与 Oracle 兼容，但参数细节需在 DM8 实测核对。

-- 先确认表名与 schema，再执行（建议非高峰）：
-- DANGER: DBMS_STATS.GATHER_TABLE_STATS('<SCHEMA>', '<TABLE>');
SELECT TABLE_NAME, LAST_ANALYZED, NUM_ROWS FROM DBA_TABLES WHERE OWNER = '<SCHEMA>' AND TABLE_NAME = '<TABLE>';
