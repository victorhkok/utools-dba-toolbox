-- 大表 / 大索引清单
-- 适用版本：11g+
-- 风险：只读
-- 说明：按MB排序
-- 提醒：只按段大小排，分区表会拆成多个段；要整表大小需按 segment_name 去掉分区后缀汇总。

SELECT *
FROM   (SELECT owner, segment_name, segment_type, tablespace_name,
               ROUND(bytes / 1024 / 1024, 2) AS mb
        FROM   dba_segments
        WHERE  segment_type IN ('TABLE', 'INDEX')
        ORDER  BY bytes DESC)
WHERE  ROWNUM <= 20;
