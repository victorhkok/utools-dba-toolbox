-- 1. 先确认表行数与统计信息（只读）：
SELECT TABLE_NAME, TABLE_ROWS, UPDATE_TIME FROM information_schema.TABLES WHERE TABLE_SCHEMA = '<DB>' AND TABLE_NAME = '<TABLE>';
-- 2. 建议非高峰执行（谨慎）：
-- DANGER: ANALYZE TABLE `<DB>`.`<TABLE>`;
