-- MGR 成员状态
-- 适用版本：8.0+
-- 风险：只读
-- 说明：performance_schema.replication_group_members
-- 大类：高可用 / 复制 / 小类：MGR / MHA
SELECT MEMBER_ID, MEMBER_HOST, MEMBER_PORT, MEMBER_STATE, MEMBER_ROLE FROM performance_schema.replication_group_members;
