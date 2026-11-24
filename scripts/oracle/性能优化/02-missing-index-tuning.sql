-- 缺失索引建议（SQL Tuning）
-- 适用版本：11g+
-- 风险：只读
-- 说明：DBMS_SQLTUNE
-- 提醒：把握一般：DBMS_SQLTUNE 需 Tuning Pack 授权，且 create_tuning_task 的返回值用法在不同版本有细节差异，生产先在测试库跑通再用。

-- 1) 建调优任务（需 Tuning Pack 授权）：
-- DECLARE l_task VARCHAR2(30);
-- BEGIN
--   l_task := DBMS_SQLTUNE.create_tuning_task(sql_id => '<sql_id>', scope => DBMS_SQLTUNE.scope_comprehensive, time_limit => 600);
--   DBMS_SQLTUNE.execute_tuning_task(task_name => l_task);
-- END;
-- /

-- 2) 查任务状态：
SELECT task_id, task_name, status, created
FROM   dba_advisor_tasks
WHERE  advisor_name = 'SQL Tuning Advisor'
ORDER  BY created DESC;

-- 3) 看报告（把 <task_name> 换成上条查到的）：
-- SELECT DBMS_SQLTUNE.report_tuning_task('<task_name>') FROM dual;
