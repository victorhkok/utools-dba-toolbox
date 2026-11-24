// uTools preload - CommonJS, Node v20.19.1
// Only expose minimal safe APIs to frontend via window.services
const core = require('./lib/sql-core.js');
const fs = require('node:fs');
const path = require('node:path');

let _toolbox = null;
function loadToolboxData() {
  if (_toolbox) return _toolbox;
  try {
    const p = path.join(__dirname, 'data', 'toolbox-filled.json');
    _toolbox = JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (e) { _toolbox = { databases: [], total_items: 0 }; }
  return _toolbox;
}
function flattenToolbox() {
  const data = loadToolboxData();
  const out = [];
  (data.databases || []).forEach((db) => {
    (db.categories || []).forEach((cat) => {
      (cat.subcategories || []).forEach((sub) => {
        (sub.items || []).forEach((it) => {
          out.push({ id: it.id, db: db.id, dbName: db.name, dbVersions: db.versions,
            category: cat.name, subcategory: sub.name, title: it.title,
            versions: it.versions, risk: it.risk, desc: it.desc || '',
            sql: it.sql || '', params: it.params || [], notes: it.notes || '' });
        });
      });
    });
  });
  return out;
}
function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
function termMatches(term, it) {
  const hay = [it.title, it.desc, it.dbName, it.category, it.subcategory, it.notes, it.versions, it.sql || ''].join(' ');
  // Pure ASCII word (RMAN/AWR/SQL): word-boundary match, so "RMAN" does not
  // match "performance_schema" in notes/SQL. Chinese terms: substring match.
  if (/^[A-Za-z0-9_]+$/.test(term)) {
    try {
      return new RegExp('(?<![A-Za-z])' + escRe(term) + '(?![A-Za-z])', 'i').test(hay);
    } catch (e) { return hay.toLowerCase().includes(term); }
  }
  return hay.toLowerCase().includes(term);
}
function searchToolbox(query, filters) {
  filters = filters || {};
  const q = (query || '').trim().toLowerCase();
  const items = flattenToolbox();
  return items.filter((it) => {
    if (filters.db && filters.db !== 'all' && it.db !== filters.db) return false;
    if (filters.category && filters.category !== 'all' && it.category !== filters.category) return false;
    if (filters.risk && filters.risk !== 'all' && it.risk !== filters.risk) return false;
    if (!q) return true;
    return q.split(/\s+/).every((w) => termMatches(w, it));
  });
}

window.services = {
  readTextFile: (filePath) => {
    try { const fs = require('node:fs'); return fs.readFileSync(filePath, 'utf8'); } catch (e) { return ''; }
  },
  formatSql: (sql, opts) => core.formatSql(sql, opts || {}),
  compressSql: (sql) => core.compressSql(sql),
  desensitizeSql: (sql) => core.desensitizeSql(sql),
  convertDialect: (sql, from, to) => core.convertDialect(sql, from, to),
  listToIn: (text, opts) => core.listToIn(text, opts || {}),
  timestampConvert: (text) => core.timestampConvert(text),

  // Toolbox: 215 scripts, loaded from data/toolbox-filled.json (local file, no network)
  loadToolbox: () => loadToolboxData(),
  searchToolbox: (query, filters) => searchToolbox(query, filters),
  getToolboxStats: () => {
    const items = flattenToolbox();
    const byDb = {};
    items.forEach((it) => { byDb[it.db] = (byDb[it.db] || 0) + 1; });
    return { total: items.length, byDb: byDb };
  },
  getScriptById: (id) => flattenToolbox().find((it) => it.id === id) || null,

  // uTools native helpers (guarded - works in uTools, no-op in plain browser preview)
  copyText: (text) => {
    try { if (typeof utools !== 'undefined' && utools.copyText) { utools.copyText(text); return true; } } catch (e) {}
    try { if (navigator && navigator.clipboard) { navigator.clipboard.writeText(text); return true; } } catch (e) {}
    return false;
  },
  hideMainWindow: () => { try { if (typeof utools !== 'undefined' && utools.hideMainWindow) utools.hideMainWindow(); } catch (e) {} },
  outPlugin: () => { try { if (typeof utools !== 'undefined' && utools.outPlugin) utools.outPlugin(); } catch (e) {} },
  getEnterAction: () => {
    try { if (typeof utools !== 'undefined' && utools.getEnterAction) return utools.getEnterAction(); } catch (e) {}
    return null;
  }
};

// Entry for keyword / regex / files modes - uTools calls window.exports.<code>
if (typeof utools !== 'undefined') {
  window.exports = {
    'sql-format': {
      mode: 'none',
      args: {
        enter: (action) => {
          // action.payload is the pasted text / file path when triggered via regex/files
          if (action && action.payload) {
            try { window.__UTOOLS_ENTER_PAYLOAD__ = action.payload; } catch (e) {}
          }
        }
      }
    },
    'sql-regex': {
      mode: 'none',
      args: {
        enter: (action) => {
          if (action && action.payload) {
            try { window.__UTOOLS_ENTER_PAYLOAD__ = action.payload; } catch (e) {}
          }
        }
      }
    },
    'sql-files': {
      mode: 'none',
      args: {
        enter: (action) => {
          if (action && action.payload) {
            try { window.__UTOOLS_ENTER_PAYLOAD__ = action.payload; } catch (e) {}
          }
        }
      }
    },
    'toolbox': {
      mode: 'none',
      args: {
        enter: (action) => {
          // Open main window on the Toolbox tab; sub-input text becomes the search query
          try { window.__UTOOLS_ENTER_CODE__ = 'toolbox'; } catch (e) {}
          if (action && action.payload) {
            try { window.__UTOOLS_ENTER_PAYLOAD__ = action.payload; } catch (e) {}
          }
        }
      }
    }
  };
}
