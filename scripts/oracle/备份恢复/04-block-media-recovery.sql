-- 块损坏 BMR 恢复
-- 适用版本：11g+
-- 风险：危险
-- 说明：BLOCKRECOVER
-- 提醒：DANGER：v$database_block_corruption 为空不代表没坏块，要 VALIDATE 才准；BLOCKRECOVER 需 RMAN 备份，没有备份无法恢复。

-- 第 1 步：先查坏块（只读）：
SELECT file#, block#, blocks, corruption_type
FROM   v$database_block_corruption
ORDER  BY file#, block#;

-- 第 2 步：校验备份（RMAN）：
-- VALIDATE DATABASE;

-- 第 3 步：块恢复模板（DANGER：需有备份，确认 file#/block# 后再执行）：
-- BLOCKRECOVER DATAFILE <file#> BLOCK <block#>;
