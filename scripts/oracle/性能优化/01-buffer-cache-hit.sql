-- Buffer Cache 命中率
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$sysstat
-- 提醒：命中率是自启动累计值，重启后清零；单看命中率不够，全表扫描多的库命中率也可能虚高，要结合 Top SQL 看。

SELECT ROUND((1 - (SELECT value FROM v$sysstat WHERE name = 'physical reads')
                    / NULLIF((SELECT value FROM v$sysstat WHERE name = 'db block gets')
                             + (SELECT value FROM v$sysstat WHERE name = 'consistent gets'), 0)) * 100, 2) AS buffer_hit_pct
FROM   dual;

SELECT name, value
FROM   v$sysstat
WHERE  name IN ('db block gets', 'consistent gets', 'physical reads', 'physical reads cache')
ORDER  BY name;
