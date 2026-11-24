-- 表 / 索引统计信息是否过期
-- 适用版本：11g+
-- 风险：只读
-- 说明：dba_tab_statistics
-- 提醒：stale_stats='YES' 只表示 10% 行变化后未收集，不等于执行计划一定差；先看具体表的慢 SQL 再决定收集。

SELECT *
FROM   (SELECT owner, table_name, num_rows, last_analyzed, stale_stats
        FROM   dba_tab_statistics
        WHERE  stale_stats = 'YES'
          AND  owner NOT IN ('SYS', 'SYSTEM', 'DBSNMP')
        ORDER  BY last_analyzed NULLS FIRST)
WHERE  ROWNUM <= 50;
