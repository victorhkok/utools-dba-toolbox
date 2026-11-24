-- 全表扫描 SQL 清单
-- 适用版本：11g+
-- 风险：只读
-- 说明：TABLE ACCESS FULL
-- 提醒：v$sql_plan 只保留共享池里的计划，重启后丢失；小表全表扫描是正常的，先看表大小和执行次数再优化。

SELECT p.sql_id,
       COUNT(*) AS full_scan_ops,
       MAX(s.executions) AS executions,
       SUBSTR(MAX(s.sql_text), 1, 200) AS sql_text
FROM   v$sql_plan p
       JOIN v$sql s ON p.sql_id = s.sql_id AND p.child_number = s.child_number
WHERE  p.operation = 'TABLE ACCESS'
  AND  p.options = 'FULL'
GROUP  BY p.sql_id
ORDER  BY full_scan_ops DESC;
