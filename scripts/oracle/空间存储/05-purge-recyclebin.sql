-- 回收站清理（PURGE）
-- 适用版本：11g+
-- 风险：谨慎
-- 说明：DROP 后恢复会失效
-- 提醒：PURGE 后 DROP 的表无法再闪回恢复；先确认 droptime 和 original_name 是要删的表，再执行。

SELECT owner, object_name, original_name, type, ts_name, droptime,
       ROUND(space * 8192 / 1024 / 1024, 2) AS mb
FROM   dba_recyclebin
ORDER  BY droptime DESC;

-- 清理模板（谨慎：PURGE 后无法 FLASHBACK 恢复）：
-- PURGE TABLE <owner>.<object_name>;
-- PURGE RECYCLEBIN;
