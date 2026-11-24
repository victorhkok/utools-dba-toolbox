-- 死锁历史（ORA-00060）
-- 适用版本：11g+
-- 风险：只读
-- 说明：alert log / trace
-- 提醒：死锁信息不在 v$ 视图里，只能看 alert 日志和 trace 文件；本条 SQL 只能定位日志路径，不能直接查出死锁 SQL。

-- 1) 查诊断目录（SQL）：
SELECT name, value
FROM   v$diag_info
WHERE  name IN ('Diag Trace', 'Diag Alert');

-- 2) 在服务器 OS 上 grep alert 日志（Shell）：
-- grep -i "ORA-00060" $ORACLE_BASE/diag/rdbms/<db_name>/<sid>/trace/alert_<sid>.log | tail -n 20
-- 3) 找到死锁 trace 文件名（alert 日志里 Deadlock graph 一节会给 trace 文件路径，再用 vi / less 打开看）
