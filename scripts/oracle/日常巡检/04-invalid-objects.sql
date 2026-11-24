-- 无效对象清单
-- 适用版本：11g+
-- 风险：只读
-- 说明：dba_objects status=INVALID
-- 提醒：只列清单不自动编译；编译用 ALTER ... COMPILE，需先确认对象属主和依赖，生产慎做。

SELECT owner, object_type, COUNT(*) AS cnt
FROM   dba_objects
WHERE  status = 'INVALID'
GROUP  BY owner, object_type
ORDER  BY cnt DESC;

-- 明细（前 50）：
SELECT *
FROM   (SELECT owner, object_name, object_type, status, last_ddl_time
        FROM   dba_objects
        WHERE  status = 'INVALID'
        ORDER  BY owner, object_type, object_name)
WHERE  ROWNUM <= 50;
