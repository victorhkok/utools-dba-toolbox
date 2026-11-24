-- 当前锁等待（sys.innodb_lock_waits）
-- 适用版本：5.7+
-- 风险：只读
-- 说明：sys 库
-- 大类：锁 / 会话 / 小类：锁
SELECT * FROM sys.innodb_lock_waits LIMIT 20;
