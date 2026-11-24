-- pg_basebackup 物理备份
-- 适用版本：12+
-- 风险：谨慎
-- 说明：流复制备份。pg_basebackup 需复制账号有 REPLICATION 权限，-X stream 才会把 WAL 一起备走。
-- 大类：备份恢复 / 小类：备份

-- shell: pg_basebackup -h <host> -U <replicator_user> -D <backup_dir> -Ft -z -P -v -X stream
-- shell: pg_basebackup -h <host> -U <replicator_user> -D <backup_dir> -Fp -P -v -X stream
