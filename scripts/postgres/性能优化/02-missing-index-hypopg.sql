-- 缺失索引（hypopg 评估）
-- 适用版本：12+
-- 风险：谨慎
-- 说明：hypopg 扩展。hypopg 是第三方扩展，需先 CREATE EXTENSION hypopg；它只做假设，不建真实索引。
-- 大类：性能优化 / 小类：索引

-- 先确认扩展：hypopg 不在 PG 核心里，需先安装
SELECT * FROM pg_extension WHERE extname = 'hypopg';
-- 模板：用参数替换表名和列名，只做假设评估，不会真建索引
-- SELECT * FROM hypopg_create_index('CREATE INDEX ON <table_name> (<column_list>)');
-- SELECT * FROM hypopg_list_indexes();
-- 评估完清理：SELECT * FROM hypopg_drop_index(<hypopg_index_oid>);
-- 再用 EXPLAIN 对比加假设索引前后的计划
