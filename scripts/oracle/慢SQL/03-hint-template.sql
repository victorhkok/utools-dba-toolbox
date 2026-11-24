-- Hint 改写模板
-- 适用版本：11g+
-- 风险：谨慎
-- 说明：/*+ INDEX / PARALLEL */ 仅模板
-- 提醒：Hint 写错表别名/索引名会被优化器静默忽略；改完务必用 DISPLAY_CURSOR 确认计划真的变了。

-- 模板（谨慎：Hint 只在确认执行计划走偏时用，先在测试库对比前后计划）：
-- SELECT /*+ INDEX(t <index_name>) */ * FROM <schema>.<table_name> t WHERE <condition>;
-- SELECT /*+ PARALLEL(t, 4) */ * FROM <schema>.<table_name> t WHERE <condition>;
-- SELECT /*+ LEADING(a b) USE_HASH(b) */ * FROM <schema>.<table_a> a, <schema>.<table_b> b WHERE a.id = b.id;

-- 查当前带 Hint 的 SQL（前 20）：
SELECT sql_id, SUBSTR(sql_text, 1, 200) AS sql_text
FROM   v$sql
WHERE  sql_text LIKE '%/*+%'
  AND  ROWNUM <= 20;
