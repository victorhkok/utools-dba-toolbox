-- 等待事件 Top 10
-- 适用版本：11g+
-- 风险：只读
-- 说明：v$system_event
-- 提醒：time_waited 单位是百分之一秒，time_waited_micro 是微秒，两者不要混用；idle 类事件已过滤，仍需结合 ASH 看。

SELECT *
FROM   (SELECT event, total_waits,
               ROUND(time_waited / 100, 2) AS waited_sec,
               ROUND(time_waited_micro / 1000000, 2) AS waited_sec_micro,
               total_timeouts
        FROM   v$system_event
        WHERE  event NOT LIKE 'SQL*Net%'
          AND  event NOT LIKE 'rdbms ipc%'
        ORDER  BY time_waited DESC)
WHERE  ROWNUM <= 10;
