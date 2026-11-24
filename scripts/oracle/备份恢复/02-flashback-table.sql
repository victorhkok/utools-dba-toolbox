-- 闪回表（FLASHBACK TABLE）
-- 适用版本：11g+
-- 风险：危险
-- 说明：需行移动开启
-- 提醒：DANGER：需先 ENABLE ROW MOVEMENT；闪回表会回退该时间点之后的所有 DML，执行前先闪回查询确认数据。

-- 第 1 步：先确认行移动是否开启（只读）：
SELECT owner, table_name, row_movement
FROM   dba_tables
WHERE  owner = '<schema>'
  AND  table_name = '<table_name>';

-- 第 2 步：确认后再执行（DANGER：会回退整表到指定时间点）：
-- ALTER TABLE <schema>.<table_name> ENABLE ROW MOVEMENT;
-- FLASHBACK TABLE <schema>.<table_name> TO TIMESTAMP TO_TIMESTAMP('<yyyy-mm-dd hh24:mi:ss>', 'YYYY-MM-DD HH24:MI:SS');
