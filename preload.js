// uTools preload - CommonJS, Node v20.19.1
// Only expose minimal safe APIs to frontend via window.services
const core = require('./lib/sql-core.js');

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
    }
  };
}
