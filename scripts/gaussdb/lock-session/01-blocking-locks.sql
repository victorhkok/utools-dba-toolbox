-- 未授权的锁（只读）：
SELECT * FROM pg_locks WHERE NOT granted;
-- 正在等锁的线程（只读）：
SELECT * FROM pg_thread_wait_status WHERE wait_status = 'acquire lock';
