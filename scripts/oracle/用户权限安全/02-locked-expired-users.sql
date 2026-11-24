-- 密码过期 / 锁定账号
-- 适用版本：11g+
-- 风险：只读
-- 说明：dba_users account_status
-- 提醒：account_status 含 EXPIRED(GRACE) 等多种状态，不等于锁定；解锁用 ALTER USER ... ACCOUNT UNLOCK，属谨慎操作勿批量执行。

SELECT username, account_status, lock_date, expiry_date, profile
FROM   dba_users
WHERE  account_status <> 'OPEN'
ORDER  BY username;

-- 即将过期（30 天内）：
SELECT username, account_status, expiry_date
FROM   dba_users
WHERE  expiry_date IS NOT NULL
  AND  expiry_date < SYSDATE + 30
ORDER  BY expiry_date;
