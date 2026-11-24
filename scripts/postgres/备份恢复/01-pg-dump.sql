-- pg_dump / pg_dumpall
-- 适用版本：12+
-- 风险：谨慎
-- 说明：逻辑备份。pg_dump 是逻辑备份，大库慢；-F c 是自定义格式，恢复用 pg_restore。
-- 大类：备份恢复 / 小类：备份

-- shell: pg_dump -h <host> -U <user> -d <db_name> -F c -f <backup_path>.dump
-- shell: pg_dump -h <host> -U <user> -d <db_name> -F p -f <backup_path>.sql
-- shell: pg_dumpall -h <host> -U <user> -f <backup_path>-globals.sql
-- shell: pg_dump --version
