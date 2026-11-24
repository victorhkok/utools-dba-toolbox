-- UNDO 使用与保留
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$undostat
-- 提醒：tuned_undoretention 是自动调优后的建议保留秒数；ORA-01555 快照过旧先看 maxquerylen 和 UNDO 大小。

SELECT tablespace_name, retention
FROM   dba_tablespaces
WHERE  contents = 'UNDO';

SELECT TO_CHAR(begin_time, 'YYYY-MM-DD HH24:MI') AS begin_time,
       undoblks, txncount, maxquerylen, tuned_undoretention
FROM   v$undostat
WHERE  begin_time >= SYSDATE - 1
ORDER  BY begin_time DESC;
