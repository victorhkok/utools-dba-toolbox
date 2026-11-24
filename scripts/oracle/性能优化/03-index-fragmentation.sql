-- 索引碎片 / 重建评估
-- 适用版本：11g+
-- 风险：谨慎
-- 说明：重建前评估锁与空间
-- 提醒：blevel>4 或 leaf_blocks 明显偏大才考虑重建；ONLINE 重建仍需空间和锁评估，碎片不高时重建收益很小。

SELECT *
FROM   (SELECT owner, index_name, table_name, blevel, leaf_blocks,
               distinct_keys, clustering_factor,
               ROUND(leaf_blocks * 8192 / 1024 / 1024, 2) AS leaf_mb
        FROM   dba_indexes
        WHERE  owner NOT IN ('SYS', 'SYSTEM')
        ORDER  BY leaf_blocks DESC)
WHERE  ROWNUM <= 20;

-- 重建模板（谨慎：先评估，勿直接执行）：
-- ALTER INDEX <owner>.<index_name> REBUILD ONLINE;
