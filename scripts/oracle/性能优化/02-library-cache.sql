-- Library Cache / 共享池
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$librarycache
-- 提醒：reloads/invalidations 持续增长说明硬解析或对象频繁失效；先查共享池和绑定变量，不要直接调大 shared_pool。

SELECT namespace, gets, gethits,
       ROUND(gethits / NULLIF(gets, 0) * 100, 2) AS gethit_pct,
       pins, pinhits,
       ROUND(pinhits / NULLIF(pins, 0) * 100, 2) AS pinhit_pct,
       reloads, invalidations
FROM   v$librarycache
ORDER  BY namespace;
