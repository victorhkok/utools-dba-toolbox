SELECT dbname, username, duration AS duration_ms, start_time, finish_time, status,
  left(query, 200) AS query_snippet
FROM gs_wlm_session_info
WHERE duration > <THRESHOLD_MS>
ORDER BY duration DESC LIMIT 20;
