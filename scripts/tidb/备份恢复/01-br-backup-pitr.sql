-- BR 全备 / PITR
-- 适用版本：6.x+
-- 风险：谨慎
-- 说明：br backup / restore
-- 备注：BR 备份/PITR 语法与存储配置需在 TiDB 6.x+ 实测核对，恢复前先在测试集群演练。

-- shell: br（TiDB 备份恢复工具，需配置存储目的端）
-- shell: br backup full --pd "http://<PD_IP>:2379" --storage "s3://<BUCKET>/<PATH>" --log-file /tmp/br.log
-- shell: br restore full --pd "http://<PD_IP>:2379" --storage "s3://<BUCKET>/<PATH>" --log-file /tmp/br-restore.log
