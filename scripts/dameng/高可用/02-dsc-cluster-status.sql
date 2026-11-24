-- DSC 集群状态
-- 适用版本：DM8+
-- 风险：只读
-- 说明：DMASM
-- 备注：DMASM/DSC 的状态查询方式需在 DM8 DSC 环境实测核对，不要凭印象执行集群命令。

-- shell: DMASM / DSC 集群状态以 DMASM 工具与 dmsvc 进程为准
-- shell: ps -ef | grep dmasm
-- shell: dmasm --help
SELECT NAME, INSTANCE_NAME, STATUS FROM V$INSTANCE;
