-- Redis 常用命令（INFO / SLOWLOG / 内存）
-- 适用版本：6.x/7.x
-- 风险：只读
-- 说明：二期
-- 备注：二期，Redis 6.x/7.x 示例命令，需按版本核对。

-- shell: redis-cli -h <HOST> -p 6379 INFO memory
-- shell: redis-cli -h <HOST> -p 6379 SLOWLOG GET 10
