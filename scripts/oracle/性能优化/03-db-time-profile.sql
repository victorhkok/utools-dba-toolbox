-- DB Time / 负载画像
-- 适用版本：11g+
-- 风险：只读
-- 说明：AWR Load Profile
-- 提醒：DB time 是所有前台会话 CPU+等待之和，可大于挂钟时间；DB time / 挂钟时间 ≈ 平均活跃会话数。

SELECT stat_name,
       ROUND(value / 1000000, 2) AS seconds
FROM   v$sys_time_model
WHERE  stat_name IN ('DB time', 'DB CPU', 'background cpu time',
                     'sql execute elapsed time', 'parse time elapsed')
ORDER  BY value DESC;

-- 另查 AWR Load Profile 需 awrrpt.sql 报告里的 Load Profile 一节，本条只给 DB Time 总量。
