-- 行锁等待详情
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$session + row_wait
-- 提醒：row_wait_* 只在会话正在等行锁时有值，锁释放后就没了；要定位行内容需按 file#/block#/row# 再查表，生产慎做。

SELECT s.sid, s.serial#, s.username, s.event, s.seconds_in_wait,
       s.row_wait_obj#, s.row_wait_file#, s.row_wait_block#, s.row_wait_row#,
       o.object_name, o.object_type
FROM   v$session s
       LEFT JOIN dba_objects o ON o.object_id = s.row_wait_obj#
WHERE  s.event LIKE 'enq: TX%'
   OR  s.wait_class = 'Application'
ORDER  BY s.seconds_in_wait DESC;
