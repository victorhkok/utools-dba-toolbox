-- 临时表空间使用
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$tempseg_usage
-- 提醒：块大小按 8K 估算，不同库块大小用 SELECT value FROM v$parameter WHERE name='db_block_size' 核对；无行返回说明当前无人用临时段。

SELECT u.username,
       s.sid,
       s.serial#,
       u.tablespace,
       u.segtype,
       u.blocks,
       ROUND(u.blocks * 8192 / 1024 / 1024, 2) AS mb_used
FROM   v$tempseg_usage u
       JOIN v$session s ON u.session_addr = s.saddr
ORDER  BY u.blocks DESC;
