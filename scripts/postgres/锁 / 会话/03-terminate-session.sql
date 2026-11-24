-- 终止会话（pg_terminate_backend）
-- 适用版本：12+
-- 风险：危险
-- 说明：先确认。先查清 pid、用户和 SQL 再杀；pg_terminate_backend 会直接断开该连接。
-- 大类：锁 / 会话 / 小类：锁

-- 第 1 步：先确认要杀的会话（长运行活跃会话）
SELECT pid, usename, application_name, client_addr, state,
       now() - query_start AS duration, left(query, 200) AS query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '5 minutes'
ORDER BY duration DESC
LIMIT 20;
-- DANGER：确认 pid 无误后再取消注释执行，杀错会话会中断业务
-- SELECT pg_terminate_backend(<pid>);
