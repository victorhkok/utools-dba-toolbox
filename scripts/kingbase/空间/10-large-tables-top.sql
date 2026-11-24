SELECT relname, sys_size_pretty(sys_total_relation_size(oid)) AS total_size
FROM sys_class
WHERE relkind = 'r'
ORDER BY sys_total_relation_size(oid) DESC
LIMIT 20;
