-- 不可见索引（8.0+）
-- 适用版本：8.0+
-- 风险：谨慎
-- 说明：Invisible Index 试索引
-- 大类：性能优化 / 小类：索引
SELECT INDEX_NAME, IS_VISIBLE FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = '<db>' AND TABLE_NAME = '<table>' LIMIT 50;
-- 设为不可见（仅 8.0+，灰度验证用）：
-- ALTER TABLE <db>.<table> ALTER INDEX <index> INVISIBLE;
-- 恢复可见：ALTER TABLE <db>.<table> ALTER INDEX <index> VISIBLE;
