-- 慢查询日志（log_min_duration）
-- 适用版本：12+
-- 风险：只读
-- 说明：postgresql.conf。log_min_duration_statement 单位是毫秒，设 1000 即只记 >1s 的；改配置用 ALTER SYSTEM + reload。
-- 大类：慢SQL / 小类：定位

SELECT name, setting, unit, context
FROM pg_settings
WHERE name IN ('log_min_duration_statement','log_statement',
               'log_directory','logging_collector','log_filename')
ORDER BY name;
-- 改阈值模板（改完 pg_reload_conf() 即可，不用重启）：
-- ALTER SYSTEM SET log_min_duration_statement = '1000';
-- SELECT pg_reload_conf();
