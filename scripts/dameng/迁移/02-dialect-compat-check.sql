-- 兼容性检查（方言差异）
-- 适用版本：DM8+
-- 风险：只读
-- 说明：NVL/ROWNUM 等
-- 备注：DBA_SOURCE 的列名需在 DM8 实测核对，ROWNUM/NVL/SYSDATE 在 DM8 多数兼容但仍需逐项核对。

-- 检查源库中 DM 不完全兼容的写法（在 Oracle 源库或迁移评估库执行）：
SELECT TOP 20 OWNER, NAME, TYPE, LINE, TEXT FROM DBA_SOURCE
WHERE TEXT LIKE '%ROWNUM%' OR TEXT LIKE '%NVL(%' OR TEXT LIKE '%SYSDATE%'
ORDER BY OWNER, NAME, LINE;
