/**
 * DBA SQL Tool - core logic (UMD: Node preload + browser index.html share same file)
 * No dependencies, no network. Pure string processing - safe to audit for uTools review.
 * Dialects: oracle | mysql | postgres | sqlserver
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.sqlCore = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var KEYWORDS = [
    'SELECT','FROM','WHERE','AND','OR','NOT','IN','IS','NULL','LIKE','BETWEEN','EXISTS',
    'GROUP','BY','ORDER','HAVING','LIMIT','OFFSET','UNION','ALL','DISTINCT','AS','ON','DESC','ASC',
    'JOIN','LEFT','RIGHT','INNER','OUTER','FULL','CROSS','CASE','WHEN','THEN','ELSE','END',
    'INSERT','INTO','VALUES','UPDATE','SET','DELETE','CREATE','TABLE','INDEX','DROP','ALTER',
    'WITH','OVER','PARTITION','ROW_NUMBER','RANK','COUNT','SUM','AVG','MAX','MIN'
  ];
  var KW_SET = {};
  KEYWORDS.forEach(function (k) { KW_SET[k] = true; });

  var CLAUSE_BREAK = ['SELECT','FROM','WHERE','GROUP BY','ORDER BY','HAVING','LIMIT','UNION','UNION ALL'];
  var JOIN_START = ['LEFT JOIN','RIGHT JOIN','INNER JOIN','OUTER JOIN','FULL JOIN','CROSS JOIN','JOIN'];

  // ---- tokenizer: keep strings / comments intact ----
  function tokenize(sql) {
    var tokens = [], i = 0, n = sql.length, buf = '';
    function flush() { if (buf.trim()) { tokens.push({ t: 'word', v: buf.trim() }); buf = ''; } }
    while (i < n) {
      var c = sql[i], next = sql[i + 1] || '';
      // line comment --
      if (c === '-' && next === '-' && (i + 2 >= n || /[\s]/.test(sql[i + 2]))) {
        flush();
        var end = sql.indexOf('\n', i); if (end === -1) end = n;
        tokens.push({ t: 'comment', v: sql.slice(i, end) }); i = end; continue;
      }
      // block comment
      if (c === '/' && next === '*') {
        flush();
        var e2 = sql.indexOf('*/', i + 2); if (e2 === -1) e2 = n - 2;
        tokens.push({ t: 'comment', v: sql.slice(i, e2 + 2) }); i = e2 + 2; continue;
      }
      // string '...' ('' escaped), "...", `...`
      if (c === "'" || c === '"' || c === '`') {
        flush();
        var q = c, j = i + 1, s = c;
        while (j < n) {
          s += sql[j];
          if (sql[j] === q) {
            if (sql[j + 1] === q) { s += sql[j + 1]; j += 2; continue; }
            j++; break;
          }
          j++;
        }
        tokens.push({ t: 'string', v: s }); i = j; continue;
      }
      if (/[\s]/.test(c)) { flush(); i++; continue; }
      if ('(),;'.indexOf(c) !== -1) { flush(); tokens.push({ t: 'punct', v: c }); i++; continue; }
      if ('=<>!+-*/%'.indexOf(c) !== -1) {
        // keep >= <= != <> || as one token
        var op = c;
        if ((c === '|' && next === '|') || (c === '<' && (next === '=' || next === '>')) ||
            (c === '>' && next === '=') || (c === '!' && next === '=') || (c === '=' && next === '=')) {
          op = c + next; i += 2;
        } else i++;
        flush(); tokens.push({ t: 'op', v: op }); continue;
      }
      buf += c; i++;
    }
    flush();
    return tokens;
  }

  function isKeyword(v) { return KW_SET[(v || '').toUpperCase()] === true; }

  function formatSql(input, opts) {
    opts = opts || {};
    var dialect = opts.dialect || 'oracle';
    var indentStr = opts.indent === 4 ? '    ' : '  ';
    var upperKw = opts.uppercaseKeywords !== false;
    if (!input || !input.trim()) return '';
    var tokens = tokenize(input);
    // Merge multi-word clauses: GROUP BY, ORDER BY, LEFT JOIN etc.
    var merged = [];
    for (var i = 0; i < tokens.length; i++) {
      var v = tokens[i].v.toUpperCase();
      var nv = tokens[i + 1] ? tokens[i + 1].v.toUpperCase() : '';
      var two = v + ' ' + nv;
      if ((v === 'GROUP' && nv === 'BY') || (v === 'ORDER' && nv === 'BY') ||
          (v === 'UNION' && nv === 'ALL') ||
          ((v === 'LEFT' || v === 'RIGHT' || v === 'INNER' || v === 'FULL' || v === 'CROSS') && nv === 'JOIN')) {
        merged.push({ t: 'word', v: two }); i++; continue;
      }
      merged.push(tokens[i]);
    }
    var lines = [], cur = '', depth = 0, inSelectList = false, lineIndent = 0;
    function pushLine() {
      var s = cur.replace(/\s+/g, ' ').trim();
      if (s) lines.push(indentStr.repeat(Math.max(0, lineIndent)) + s);
      cur = ''; lineIndent = depth;
    }
    merged.forEach(function (tok, idx) {
      var raw = tok.v, up = raw.toUpperCase();
      if (tok.t === 'punct' && raw === '(') {
        // subquery: SELECT ( ... ) -> newline + indent
        var prev = merged[idx - 1];
        var isSub = prev && (prev.v.toUpperCase() === 'FROM' || prev.v.toUpperCase() === 'IN' || prev.v.toUpperCase() === 'JOIN');
        var isFunc = prev && prev.t === 'word' && !CLAUSE_BREAK.includes(prev.v.toUpperCase()) && !JOIN_START.includes(prev.v.toUpperCase());
        if (isFunc) cur = cur.replace(/\s+$/, '') + '('; // COUNT(*) not COUNT (*)
        else cur += (cur && !cur.endsWith(' ') ? ' ' : '') + '(';
        if (isSub) { pushLine(); depth++; lineIndent = depth; }
        else depth++;
        return;
      }
      if (tok.t === 'punct' && raw === ')') {
        depth = Math.max(0, depth - 1);
        cur = cur.replace(/\s+$/, '') + ')';
        return;
      }
      // * inside function call: COUNT(*) not COUNT( * )
      if (tok.t === 'op' && raw === '*' && cur.endsWith('(')) { cur += '*'; return; }
      if (tok.t === 'punct' && raw === ';') { cur += ';'; pushLine(); return; }
      if (tok.t === 'punct' && raw === ',') {
        cur += ',';
        // comma inside SELECT list -> newline; inside function call keep inline
        if (inSelectList && depth === 0) pushLine();
        else cur += ' ';
        return;
      }
      if (tok.t === 'comment') { pushLine(); lines.push(indentStr.repeat(Math.max(0, lineIndent)) + raw); return; }
      // Clause break
      if (tok.t === 'word' && CLAUSE_BREAK.indexOf(up) !== -1) {
        pushLine();
        if (up === 'SELECT') inSelectList = true;
        if (up === 'FROM' || up === 'WHERE') inSelectList = false;
        cur = up; return;
      }
      if (tok.t === 'word' && JOIN_START.indexOf(up) !== -1) {
        pushLine(); cur = up; inSelectList = false; return;
      }
      if (tok.t === 'word' && (up === 'AND' || up === 'OR')) {
        pushLine(); cur = up + ' '; return;
      }
      // Normal word
      var word = upperKw && isKeyword(raw) ? up : raw;
      // Preserve original case for identifiers, only upper keywords
      if (tok.t === 'word' && !isKeyword(raw)) word = raw;
      if (tok.t === 'string') word = raw;
      cur += (cur ? ' ' : '') + word;
    });
    pushLine();
    var out = lines.join('\n');
    // dialect hint in comment footer is added by UI, not here
    return out.replace(/\n{3,}/g, '\n\n').trim() + (input.trim().endsWith(';') ? '' : '');
  }

  function compressSql(input) {
    if (!input) return '';
    return tokenize(input).map(function (t) { return t.v; }).join(' ').replace(/\s+([,;()])/g, '$1').replace(/([(])\s+/g, '$1').trim();
  }

  function desensitizeSql(input) {
    if (!input) return '';
    var tokens = tokenize(input);
    return tokens.map(function (t) {
      if (t.t === 'string') return "'***'";
      if (t.t === 'word' && /^\d+(\.\d+)?$/.test(t.v)) return '?';
      return t.v;
    }).join(' ')
      .replace(/\s+([,;()])/g, '$1').replace(/([(])\s+/g, '$1')
      // also mask numbers after = / IN (...)
      .replace(/=\s*\?/g, '= ?');
  }

  // Oracle <-> MySQL (rule-based, NOT a full transpiler - UI must warn to verify)
  var ORACLE_TO_MYSQL = [
    [/NVL\s*\(/gi, 'IFNULL('],
    [/\bSYSDATE\b/gi, 'NOW()'],
    [/\bSYSTIMESTAMP\b/gi, 'NOW(6)'],
    [/TO_CHAR\s*\(\s*([^,]+?)\s*,\s*'YYYY-MM-DD HH24:MI:SS'\s*\)/gi, "DATE_FORMAT($1, '%Y-%m-%d %H:%i:%s')"],
    [/TO_CHAR\s*\(\s*([^,]+?)\s*,\s*'YYYY-MM-DD'\s*\)/gi, "DATE_FORMAT($1, '%Y-%m-%d')"],
    [/TO_DATE\s*\(\s*'([^']+)'\s*,\s*'YYYY-MM-DD'\s*\)/gi, "STR_TO_DATE('$1', '%Y-%m-%d')"],
    [/\bDUAL\b/gi, 'DUAL'],
    [/\|\|/g, ' CONCAT '], // rough: a || b -> CONCAT - user must check parentheses
    [/\bROWNUM\s*<=\s*(\d+)/gi, 'LIMIT $1 /* 原 ROWNUM <= $1, 需确认 ORDER BY 后再 LIMIT */'],
    [/\bVARCHAR2\b/gi, 'VARCHAR'],
    [/\bNUMBER\s*\(\s*(\d+)\s*\)/gi, 'DECIMAL($1,0)'],
    [/\bNUMBER\b/gi, 'DECIMAL(10,0)'],
    [/SEQUENCE\.NEXTVAL/gi, '/* 序列 NEXTVAL -> MySQL 用 AUTO_INCREMENT, 需手动改 */ NULL'],
  ];
  var MYSQL_TO_ORACLE = [
    [/IFNULL\s*\(/gi, 'NVL('],
    [/\bNOW\(\)/gi, 'SYSDATE'],
    [/DATE_FORMAT\s*\(\s*([^,]+?)\s*,\s*'%Y-%m-%d %H:%i:%s'\s*\)/gi, "TO_CHAR($1, 'YYYY-MM-DD HH24:MI:SS')"],
    [/DATE_FORMAT\s*\(\s*([^,]+?)\s*,\s*'%Y-%m-%d'\s*\)/gi, "TO_CHAR($1, 'YYYY-MM-DD')"],
    [/STR_TO_DATE\s*\(\s*'([^']+)'\s*,\s*'%Y-%m-%d'\s*\)/gi, "TO_DATE('$1', 'YYYY-MM-DD')"],
    [/`([^`]+)`/g, '"$1"'],
    [/\bLIMIT\s+(\d+)\s*$/gi, '/* 原 LIMIT $1 -> Oracle: WHERE ROWNUM <= $1 或 FETCH FIRST $1 ROWS ONLY */'],
    [/\bAUTO_INCREMENT\b/gi, '/* AUTO_INCREMENT -> Oracle 12c+ 用 GENERATED AS IDENTITY */'],
    [/\bUNSIGNED\b/gi, ''],
  ];

  function convertDialect(input, from, to) {
    if (!input) return { sql: '', warnings: [] };
    if (from === to) return { sql: input, warnings: ['源方言与目标方言相同，未做转换'] };
    var rules = (from === 'oracle' && to === 'mysql') ? ORACLE_TO_MYSQL
      : (from === 'mysql' && to === 'oracle') ? MYSQL_TO_ORACLE : null;
    if (!rules) return { sql: input, warnings: ['v0.1 只支持 Oracle <-> MySQL 互转，其他方言仅做格式化'] };
    var out = input, warnings = [];
    rules.forEach(function (r) { out = out.replace(r[0], r[1]); });
    if (/CONCAT/.test(out) && from === 'oracle') warnings.push('|| 已粗转为 CONCAT，含多个 || 时需手动加括号核对');
    if (/ROWNUM|LIMIT|序列|AUTO_INCREMENT/.test(out)) warnings.push('ROWNUM / LIMIT / 序列 / 自增语义不同，已在注释中标注，请人工核对');
    if (/TO_CHAR|DATE_FORMAT|TO_DATE|STR_TO_DATE/.test(out)) warnings.push('日期格式函数已按常见格式映射，非常用格式请核对');
    warnings.push('规则式转换非完整转译，上线前请在测试库跑一遍');
    return { sql: out, warnings: warnings };
  }

  function listToIn(input, opts) {
    opts = opts || {};
    var items = input.split(/[\n,，;；\t]+/).map(function (s) { return s.trim(); }).filter(Boolean);
    if (opts.dedup !== false) items = Array.from(new Set(items));
    if (!items.length) return { sql: '', count: 0, warning: '' };
    var allNum = items.every(function (s) { return /^-?\d+(\.\d+)?$/.test(s); });
    var quoted = items.map(function (s) {
      if (allNum) return s;
      return "'" + s.replace(/'/g, "''") + "'";
    });
    var warning = '';
    if (quoted.length > 1000) warning = 'Oracle IN 列表超过 1000 个会报 ORA-01795，建议分批或改用临时表 / JOIN';
    if (quoted.length > 100) warning = warning || '数量较多（' + quoted.length + ' 个），建议确认是否改用临时表';
    return { sql: 'IN (' + quoted.join(', ') + ')', count: quoted.length, warning: warning };
  }

  function timestampConvert(input) {
    var s = (input || '').trim();
    if (!s) return { out: '', hint: '' };
    // Unix timestamp
    if (/^\d{10}$/.test(s)) {
      var d = new Date(parseInt(s, 10) * 1000);
      return { out: fmtDate(d) + ' (本地时间)', hint: '10 位秒级时间戳' };
    }
    if (/^\d{13}$/.test(s)) {
      var d2 = new Date(parseInt(s, 10));
      return { out: fmtDate(d2) + ' (本地时间)', hint: '13 位毫秒级时间戳' };
    }
    // YYYY-MM-DD HH:mm:ss -> timestamp
    var m = s.match(/^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?/);
    if (m) {
      var dt = new Date(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0), +(m[6] || 0));
      return { out: '秒: ' + Math.floor(dt.getTime() / 1000) + '  /  毫秒: ' + dt.getTime(), hint: '日期 -> 时间戳（本地时区）' };
    }
    return { out: '', hint: '无法识别：支持 10/13 位时间戳，或 YYYY-MM-DD HH:mm:ss' };
  }
  function fmtDate(d) {
    function p(n) { return String(n).padStart(2, '0'); }
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
  }

  return {
    formatSql: formatSql, compressSql: compressSql, desensitizeSql: desensitizeSql,
    convertDialect: convertDialect, listToIn: listToIn, timestampConvert: timestampConvert,
    tokenize: tokenize
  };
});
