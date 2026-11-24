-- MGR 主节点切换
-- 适用版本：8.0+
-- 风险：危险
-- 说明：group_replication_set_as_primary
-- 大类：高可用 / 复制 / 小类：MGR / MHA
-- 先查当前主节点 UUID：
SELECT MEMBER_ID, MEMBER_HOST, MEMBER_ROLE FROM performance_schema.replication_group_members;
-- DANGER: 切换主节点，先确认业务影响和新主已同步：
-- SELECT group_replication_set_as_primary('<primary_uuid>');
