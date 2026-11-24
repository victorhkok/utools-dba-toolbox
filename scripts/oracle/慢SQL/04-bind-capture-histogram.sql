-- 绑定变量窥探 / 直方图检查
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$sql_bind_capture
-- 提醒：v$sql_bind_capture 只保留最近一次捕获的绑定值，不代表每次执行的值；直方图过期会导致绑定窥探失真。

SELECT sql_id, name, position, datatype_string, value_string, last_captured
FROM   v$sql_bind_capture
WHERE  sql_id = '<sql_id>'
ORDER  BY position;

-- 直方图（只列有直方图的列）：
SELECT owner, table_name, column_name, histogram, num_distinct
FROM   dba_tab_col_statistics
WHERE  histogram <> 'NONE'
  AND  owner = '<schema>'
ORDER  BY table_name, column_name;
