-- 告警日志近24h错误
-- 适用版本：11g+
-- 风险：只读
-- 说明：需读alert log / ADRCI
-- 提醒：ADRCI 的 homepath 按实际 diag 路径填；alert 日志不在数据库里，SQL 查不到内容，只能查路径。

-- 1) 先查诊断目录（SQL）：
SELECT name, value
FROM   v$diag_info
WHERE  name IN ('Diag Trace', 'Diag Alert', 'Diag Incident');

-- 2) 再在服务器 OS 用 ADRCI（Shell）：
-- adrci exec="set homepath diag/rdbms/<db_name>/<sid>; show alert -term -tail 200"
-- 3) 常见错误直接 grep alert 日志：
-- grep -E "ORA-|TNS-" $ORACLE_BASE/diag/rdbms/<db_name>/<sid>/trace/alert_<sid>.log | tail -n 100
