-- 闪回查询（AS OF TIMESTAMP）
-- 适用版本：11g+
-- 风险：只读
-- 说明：需UNDO保留
-- 提醒：超过 UNDO 保留期会报 ORA-01555；闪回查询只能读，不能直接 UPDATE 回去，要恢复需 INSERT SELECT。

-- 查 1 小时前的数据（模板）：
SELECT * FROM <schema>.<table_name> AS OF TIMESTAMP (SYSDATE - 1 / 24) WHERE ROWNUM <= 20;

-- 先确认 UNDO 能保留多久（只读）：
SELECT TO_CHAR(begin_time, 'YYYY-MM-DD HH24:MI') AS begin_time,
       tuned_undoretention, maxquerylen
FROM   v$undostat
WHERE  begin_time >= SYSDATE - 1
ORDER  BY begin_time DESC;
