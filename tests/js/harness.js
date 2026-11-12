/* Loads shared/templates/core.js (and optionally i18n.js, viz.js) in a stub DOM so the pure-string
   functions (ALS.md, ALS.tex, ALS.t) can be tested with plain Node: node tests/js/test_core.js */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..', '..');

function load(files, i18n) {
  const el = () => ({ getAttribute() { return null; }, setAttribute() {}, style: {}, classList: { add() {}, remove() {}, toggle() {} }, appendChild() {} });
  const document = Object.assign(el(), { documentElement: el(), head: el(), body: el(), addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; }, createElement: el });
  const window = { ALS_THEMES: {}, ALS_I18N: i18n || {}, matchMedia: null, addEventListener() {}, innerWidth: 1200 };
  const ctx = { window, document, localStorage: { getItem() { return null; }, setItem() {} }, console, setTimeout, clearTimeout, setInterval() {}, Event: function () {}, URLSearchParams };
  vm.createContext(ctx);
  for (const f of files) vm.runInContext(fs.readFileSync(path.join(ROOT, 'shared', 'templates', f), 'utf8'), ctx, { filename: f });
  return ctx.window;
}

/* Replace maths spans by ⟦tex⟧ (inline) or ⟦⟦tex⟧⟧ (display) so expectations stay readable. */
function show(html) {
  const un = (t) => t.replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
  return html.replace(/<span class="als-math[^"]*" data-display="(\d)" data-tex="([^"]*)">[^<]*<\/span>/g,
    (m, d, t) => (d === '1' ? '⟦⟦' : '⟦') + un(t).trim() + (d === '1' ? '⟧⟧' : '⟧'));
}

module.exports = { load, show, ROOT };
