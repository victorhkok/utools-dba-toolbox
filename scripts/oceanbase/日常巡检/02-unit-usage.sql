-- 资源单元（Unit）使用
-- 适用版本：4.x
-- 风险：只读
-- 说明：__all_unit
-- 备注：__all_unit 的内存单位与列名需在 OB 4.x 实测核对。

SELECT UNIT_ID, TENANT_ID, ZONE, SVR_IP, MAX_CPU, MIN_CPU, MEMORY_SIZE/1024/1024 AS MEMORY_MB, STATUS
FROM oceanbase.__all_unit
ORDER BY TENANT_ID, ZONE LIMIT 20;
