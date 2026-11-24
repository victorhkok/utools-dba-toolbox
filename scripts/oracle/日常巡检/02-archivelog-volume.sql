-- 归档日志生成量 / 切换频率
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$archived_log
-- 提醒：v$archived_log 只保留控制文件记录的归档，控制文件被覆盖后旧记录会丢；长期趋势以备份/监控为准。

SELECT TRUNC(first_time) AS day,
       COUNT(*)             AS arch_count,
       ROUND(SUM(blocks * block_size) / 1024 / 1024, 2) AS mb_generated
FROM   v$archived_log
WHERE  first_time >= SYSDATE - 7
GROUP  BY TRUNC(first_time)
ORDER  BY day DESC;

-- 日志切换次数（近 7 天，按天）：
SELECT TRUNC(first_time) AS day, COUNT(*) AS switch_count
FROM   v$log_history
WHERE  first_time >= SYSDATE - 7
GROUP  BY TRUNC(first_time)
ORDER  BY day DESC;
