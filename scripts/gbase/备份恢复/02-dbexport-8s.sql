-- 8s 逻辑备份（dbexport）
-- 适用版本：8s
-- 风险：谨慎
-- 说明：dbexport
-- 备注：dbexport 参数需在 8s 实测核对，备份前确认磁盘余量。

-- shell: dbexport（GBase 8s / Informix 兼容逻辑备份）
-- shell: dbexport -d <DATABASE> -o <备份目录>
