-- 段增长 Top 20
-- 适用版本：11g+
-- 风险：只读
-- 说明：dba_segments
-- 提醒：dba_segments 是当前大小，不是增长量；要增长趋势需定期快照对比，或查 dba_hist_seg_stat（需 Diagnostic Pack）。

SELECT *
FROM   (SELECT owner, segment_name, segment_type, tablespace_name,
               ROUND(bytes / 1024 / 1024, 2) AS mb
        FROM   dba_segments
        ORDER  BY bytes DESC)
WHERE  ROWNUM <= 20;
