-- 未使用索引清单
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$object_usage，需先监控
-- 提醒：v$object_usage 只有开过 MONITORING USAGE 的索引才有行；没监控过查不到不等于没用，勿直接删索引。

SELECT index_name, table_name, monitoring, used,
       start_monitoring, end_monitoring
FROM   v$object_usage
WHERE  used = 'NO'
ORDER  BY table_name, index_name;

-- 开启监控（需先执行，跑一个业务周期后再查上条）：
-- ALTER INDEX <owner>.<index_name> MONITORING USAGE;
