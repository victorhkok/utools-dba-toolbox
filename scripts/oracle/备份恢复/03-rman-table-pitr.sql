-- RMAN 表级 PITR
-- 适用版本：12c+
-- 风险：危险
-- 说明：12c+支持，4-12h
-- 提醒：仅 12c+ 支持，11g 跑会报错；AUXILIARY DESTINATION 需有足够空间放辅助实例，恢复耗时按表大小估算。

-- 12c+ 才支持 RECOVER TABLE，先确认版本和备份（只读）：
-- SELECT * FROM v$version;
-- LIST BACKUP OF TABLE <schema>.<table_name>;

-- 恢复模板（DANGER：只在演练/恢复场景执行，12c+）：
-- RECOVER TABLE <schema>.<table_name>
--   UNTIL TIME "TO_DATE('<yyyy-mm-dd hh24:mi:ss>', 'YYYY-MM-DD HH24:MI:SS')"
--   AUXILIARY DESTINATION '<aux_dir>';
