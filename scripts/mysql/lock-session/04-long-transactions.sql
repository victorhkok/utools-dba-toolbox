-- 长事务（>30min）
-- 适用版本：5.7+
-- 风险：只读
-- 说明：information_schema.INNODB_TRX
-- 大类：锁 / 会话 / 小类：锁
SELECT trx_id, trx_state, trx_started, trx_mysql_thread_id, trx_query FROM information_schema.INNODB_TRX WHERE trx_started < NOW() - INTERVAL 30 MINUTE LIMIT 20;
