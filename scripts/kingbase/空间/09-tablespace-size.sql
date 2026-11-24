SELECT spcname, sys_size_pretty(sys_tablespace_size(spcname)) AS size
FROM sys_tablespace
ORDER BY sys_tablespace_size(spcname) DESC;
