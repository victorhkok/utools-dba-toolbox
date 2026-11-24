-- ibdata / undo / redo 大小
-- 适用版本：5.7+
-- 风险：只读
-- 说明：SHOW VARIABLES
-- 大类：空间 / 存储 / 小类：空间
SHOW VARIABLES LIKE 'innodb_data_file_path';
SHOW VARIABLES LIKE 'innodb_data_home_dir';
SHOW VARIABLES LIKE 'innodb_undo_directory';
SHOW VARIABLES LIKE 'innodb_log_file_size';
SHOW VARIABLES LIKE 'innodb_log_files_in_group';
SHOW VARIABLES LIKE 'innodb_log_group_home_dir';
