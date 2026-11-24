-- 数据库 / PDB 列表
-- 适用版本：12c+
-- 风险：只读
-- 说明：CDB+PDB，11g无PDB
-- 提醒：仅 12c+ 有 v$pdbs / CDB 概念，11g 跑第二条会报 ORA-00942；先查 v$database.cdb 确认是否 CDB。

SELECT name, cdb, open_mode, log_mode
FROM   v$database;

SELECT con_id, name, open_mode, restricted, total_size
FROM   v$pdbs
ORDER  BY con_id;
