-- mydumper 并行备份
-- 适用版本：5.7+
-- 风险：谨慎
-- 说明：大库首选
-- 大类：备份恢复 / 小类：逻辑备份
-- shell: mydumper -u <user> -B <db> -o "<backup_dir>" -t 4 --routines --events --triggers --compress
-- shell: 恢复用 myloader -u <user> -d "<backup_dir>" -t 4
-- 备份前先确认：
SHOW BINARY LOGS;
