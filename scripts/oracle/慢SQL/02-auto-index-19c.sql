-- 自动索引建议（19c+）
-- 适用版本：19c+
-- 风险：谨慎
-- 说明：DBMS_AUTO_INDEX
-- 提醒：把握一般：DBA_AUTO_INDEX_CONFIG 的列名/参数名在 19c 各补丁间有细节差异，且自动索引默认不开启；本条先以查询为准，开启前务必在测试库核对视图定义。

-- 查自动索引配置：
SELECT parameter_name, parameter_value
FROM   dba_auto_index_config
ORDER  BY parameter_name;

-- 查已自动创建的索引：
SELECT index_name, table_owner, table_name, auto
FROM   dba_indexes
WHERE  auto = 'YES'
ORDER  BY table_name;

-- 查最近自动索引活动报告：
-- SELECT DBMS_AUTO_INDEX.report_last_activity() FROM dual;
