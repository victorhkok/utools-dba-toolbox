-- MongoDB 慢查询 / 索引
-- 适用版本：6.x/7.x
-- 风险：只读
-- 说明：二期
-- 备注：二期，MongoDB 6.x/7.x 示例命令，需按版本核对。

// MongoDB shell:
db.currentOp({ "active": true, "secs_running": { "$gt": 5 } });
db.<COLLECTION>.getIndexes();
