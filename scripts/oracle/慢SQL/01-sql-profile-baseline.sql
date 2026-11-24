-- SQL Profile / Baseline 建议
-- 适用版本：11g+
-- 风险：谨慎
-- 说明：SQL Tuning Advisor
-- 提醒：接受 Profile 会改变执行计划，生产先在测试库验证；Baseline 需先用 DBMS_SPM.load_plans_from_cursor_cache 加载。

-- 1) 先跑调优任务并看报告（见“缺失索引建议”那条，任务名换成实际值）：
-- SELECT DBMS_SQLTUNE.report_tuning_task('<task_name>') FROM dual;

-- 2) 查已有 Profile / Baseline：
SELECT name, type, status, created
FROM   dba_sql_profiles
ORDER  BY created DESC;

SELECT sql_handle, plan_name, enabled, accepted, origin
FROM   dba_sql_plan_baselines
ORDER  BY created DESC;

-- 3) 接受 Profile 模板（谨慎：先在测试库验证）：
-- EXEC DBMS_SQLTUNE.accept_sql_profile(task_name => '<task_name>', name => '<profile_name>');
