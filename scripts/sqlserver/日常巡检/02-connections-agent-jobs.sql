-- 连接 / 作业（Agent Job）状态
-- 适用版本：2016+
-- 风险：只读
-- 说明：msdb.dbo.sysjobs。sys.dm_exec_sessions 只看用户会话，作业状态在 msdb 的 sysjobs/sysjobactivity。
-- 大类：日常巡检 / 小类：实例

SELECT login_name, host_name, program_name, count(*) AS session_count
FROM sys.dm_exec_sessions
WHERE is_user_process = 1
GROUP BY login_name, host_name, program_name
ORDER BY session_count DESC;
SELECT TOP 20 j.name AS job_name, j.enabled,
       ja.run_requested_date, ja.stop_execution_date
FROM msdb.dbo.sysjobs AS j
LEFT JOIN msdb.dbo.sysjobactivity AS ja
  ON ja.job_id = j.job_id
ORDER BY j.name;
