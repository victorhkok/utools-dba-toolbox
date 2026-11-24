-- shared_buffers / work_mem 建议
-- 适用版本：12+
-- 风险：只读
-- 说明：SHOW。只读查询参数，不改配置；调参要结合内存总量和连接数，改完需 reload/重启看 context。
-- 大类：性能优化 / 小类：参数与缓存

SELECT name, setting, unit, context, short_desc
FROM pg_settings
WHERE name IN ('shared_buffers','work_mem','maintenance_work_mem',
               'effective_cache_size','max_connections')
ORDER BY name;
SHOW shared_buffers;
SHOW work_mem;
