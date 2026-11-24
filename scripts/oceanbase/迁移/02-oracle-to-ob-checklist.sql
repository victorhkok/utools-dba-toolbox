-- Oracle → OB 迁移清单
-- 适用版本：4.x
-- 风险：谨慎
-- 说明：OMS / 数据类型映射
-- 备注：迁移以 OMS 工具为准，序列、同义词、存储过程等对象需逐项核对。

-- 迁移前检查（只读，Oracle 模式）：
SELECT OWNER, OBJECT_TYPE, COUNT(*) AS CNT FROM DBA_OBJECTS GROUP BY OWNER, OBJECT_TYPE ORDER BY CNT DESC FETCH FIRST 20 ROWS ONLY;
-- 需在 OB 4.x 实测核对 DBA_OBJECTS 在 Oracle 模式下的可用性，数据类型映射以 OMS 评估报告为准。
