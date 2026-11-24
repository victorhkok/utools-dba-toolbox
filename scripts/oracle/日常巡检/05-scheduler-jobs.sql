-- 定时任务 / 作业状态
-- 适用版本：11g+
-- 风险：只读
-- 说明：dba_scheduler_jobs
-- 提醒：state=BROKEN/FAILURE 重点看；查单作业失败明细用 dba_scheduler_job_run_details。

SELECT owner, job_name, job_type, state, enabled,
       last_start_date, next_run_date, failure_count
FROM   dba_scheduler_jobs
WHERE  owner NOT IN ('SYS', 'SYSTEM')
ORDER  BY owner, job_name;
