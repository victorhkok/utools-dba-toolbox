-- 审计开启与审计日志
-- 适用版本：11g+
-- 风险：只读
-- 说明：11g审计 / 12c+统一审计
-- 提醒：11g 用 dba_audit_trail，12c+ 推荐 unified_audit_trail；SHOW PARAMETER 是 SQL*Plus 命令，在 JDBC 里跑不了。

-- 1) 查审计开关（SQL*Plus）：
-- SHOW PARAMETER audit_trail;

-- 2) 11g 传统审计日志（近 1 天，前 50）：
SELECT username, action_name, timestamp, obj_name, returncode
FROM   dba_audit_trail
WHERE  timestamp >= SYSDATE - 1
  AND  ROWNUM <= 50
ORDER  BY timestamp DESC;

-- 3) 12c+ 统一审计（仅 12c+，11g 跑会报 ORA-00942）：
-- SELECT dbusername, action_name, event_timestamp, object_name, return_code
-- FROM   unified_audit_trail
-- WHERE  event_timestamp >= SYSDATE - 1
--   AND  ROWNUM <= 50
-- ORDER  BY event_timestamp DESC;
