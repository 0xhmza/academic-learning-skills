/* ALS core runtime, shared by every template and inlined at build time.
   Provides: data loading, theme + light/dark switching, safe Markdown-lite with KaTeX maths,
   code highlighting, SVG sanitising, storage, downloads, keyboard helpers and the top bar. */
(function () {
  'use strict';

  var ALS = (window.ALS = window.ALS || {});
  var THEMES = window.ALS_THEMES || {};
  var KATEX = 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.11/';

  /* ---------------- small helpers ---------------- */
  ALS.$ = function (sel, root) { return (root || document).querySelector(sel); };
  ALS.$$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  ALS.esc = function (s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  ALS.el = function (tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v == null || v === false) return;
        if (k === 'class') node.className = v;
        else if (k === 'html') node.innerHTML = v;
        else if (k === 'text') node.textContent = v;
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') node.addEventListener(k.slice(2), v);
        else node.setAttribute(k, v === true ? '' : v);
      });
    }
    (children || []).forEach(function (c) {
      if (c == null) return;
      node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return node;
  };

  ALS.slug = function (s) {
    return String(s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'item';
  };

  ALS.today = function () {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  };

  ALS.shuffle = function (arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  };

  ALS.download = function (filename, content, mime) {
    var blob = new Blob([content], { type: mime || 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = ALS.el('a', { href: url, download: filename });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  };

  ALS.toast = function (msg) {
    var t = ALS.$('#als-toast');
    if (!t) {
      t = ALS.el('div', { id: 'als-toast', role: 'status', 'aria-live': 'polite', class: 'als-toast' });
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.setAttribute('data-show', 'true');
    clearTimeout(ALS._toastTimer);
    ALS._toastTimer = setTimeout(function () { t.removeAttribute('data-show'); }, 2200);
  };

  /* ---------------- storage (never required to work) ---------------- */
  ALS.store = {
    key: function (k) { return 'als:' + ALS.pageKey + ':' + k; },
    get: function (k, fallback) {
      try { var v = localStorage.getItem(ALS.store.key(k)); return v == null ? fallback : JSON.parse(v); }
      catch (e) { return fallback; }
    },
    set: function (k, v) { try { localStorage.setItem(ALS.store.key(k), JSON.stringify(v)); } catch (e) { /* private mode */ } },
    del: function (k) { try { localStorage.removeItem(ALS.store.key(k)); } catch (e) { /* ignore */ } },
    globalGet: function (k, fallback) { try { var v = localStorage.getItem('als:' + k); return v == null ? fallback : v; } catch (e) { return fallback; } },
    globalSet: function (k, v) { try { localStorage.setItem('als:' + k, v); } catch (e) { /* ignore */ } }
  };

  /* ---------------- Markdown-lite + maths ---------------- */
  var MATH_RE = /\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$(?!\s)((?:\\\$|[^$\n])+?)(?<!\s)\$(?!\d)/g;

  ALS.hasMath = function (s) { MATH_RE.lastIndex = 0; return MATH_RE.test(String(s || '')); };

  function mathSpan(tex, display) {
    return '<span class="als-math' + (display ? ' als-math-display' : '') + '" data-display="' + (display ? 1 : 0) +
      '" data-tex="' + ALS.esc(tex) + '">' + ALS.esc(display ? tex : tex) + '</span>';
  }

  function inline(s) {
    // s is already escaped. Order matters: links, bold, italic.
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, function (_, t, u) {
      return '<a href="' + u + '" target="_blank" rel="noopener noreferrer">' + t + '</a>';
    });
    s = s.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/(^|[^*\w])\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\w)/g, '$1<em>$2</em>');
    s = s.replace(/(^|[\s(])_(?!\s)([^_\n]+?)(?<!\s)_(?=[\s).,;:!?]|$)/g, '$1<em>$2</em>');
    return s;
  }

  /* Render a rich-text string to safe HTML. opts.inline = no paragraph wrapping. */
  ALS.md = function (text, opts) {
    opts = opts || {};
    if (text == null) return '';
    var store = [];
    var hold = function (html) { store.push(html); return '\u0000' + (store.length - 1) + '\u0000'; };
    var s = String(text).replace(/\r\n?/g, '\n');

    s = s.replace(/`([^`\n]+)`/g, function (_, c) { return hold('<code>' + ALS.esc(c) + '</code>'); });
    s = s.replace(MATH_RE, function (m, d1, d2, i1, i2) {
      if (d1 != null || d2 != null) return hold(mathSpan((d1 != null ? d1 : d2).trim(), true));
      return hold(mathSpan((i1 != null ? i1 : i2).trim(), false));
    });
    s = ALS.esc(s);

    var out;
    if (opts.inline) {
      out = inline(s).replace(/\n/g, '<br>');
    } else {
      out = s.split(/\n{2,}/).map(function (block) {
        var lines = block.split('\n');
        if (lines.every(function (l) { return /^\s*[-*•]\s+/.test(l); })) {
          return '<ul>' + lines.map(function (l) { return '<li>' + inline(l.replace(/^\s*[-*•]\s+/, '')) + '</li>'; }).join('') + '</ul>';
        }
        if (lines.every(function (l) { return /^\s*\d+[.)]\s+/.test(l); })) {
          return '<ol>' + lines.map(function (l) { return '<li>' + inline(l.replace(/^\s*\d+[.)]\s+/, '')) + '</li>'; }).join('') + '</ol>';
        }
        var trimmed = block.trim();
        if (/^\u0000\d+\u0000$/.test(trimmed) && store[+trimmed.slice(1, -1)].indexOf('als-math-display') > -1) return trimmed;
        return '<p>' + inline(block).replace(/\n/g, '<br>') + '</p>';
      }).join('');
    }
    return out.replace(/\u0000(\d+)\u0000/g, function (_, i) { return store[+i]; });
  };

  /* Set rich HTML on an element and typeset its maths. */
  ALS.rich = function (node, text, opts) {
    node.innerHTML = ALS.md(text, opts);
    if (!opts || !opts.noClass) node.classList.add('als-rich');
    ALS.renderMath(node);
    return node;
  };

  ALS.renderMath = function (root) {
    var nodes = ALS.$$('.als-math:not([data-done])', root || document);
    if (!nodes.length) return;
    if (!window.katex) {
      nodes.forEach(function (n) { n.classList.add('als-math-raw'); });
      ALS.loadKatex();
      return;
    }
    nodes.forEach(function (n) {
      try {
        window.katex.render(n.getAttribute('data-tex'), n, { displayMode: n.getAttribute('data-display') === '1', throwOnError: false, strict: 'ignore', macros: ALS.macros });
        n.classList.remove('als-math-raw');
        n.setAttribute('data-done', '1');
      } catch (e) { n.classList.add('als-math-raw'); }
    });
  };

  ALS.loadKatex = function () {
    if (ALS._katexLoading || window.katex) return;
    ALS._katexLoading = true;
    document.head.appendChild(ALS.el('link', { rel: 'stylesheet', href: KATEX + 'katex.min.css', crossorigin: 'anonymous' }));
    var sc = ALS.el('script', { src: KATEX + 'katex.min.js', crossorigin: 'anonymous', defer: true });
    sc.onload = function () { ALS.renderMath(document); document.dispatchEvent(new Event('als:math')); };
    sc.onerror = function () { /* offline: TeX stays readable as raw text */ };
    document.head.appendChild(sc);
  };

  /* ---------------- code highlighting (small, generic) ---------------- */
  var KW = {
    py: 'and as assert async await break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return True try while with yield match case self',
    js: 'async await break case catch class const continue debugger default delete do else export extends false finally for from function if import in instanceof let new null of return super switch this throw true try typeof undefined var void while yield interface type enum implements',
    c: 'auto break case char const continue default do double else enum extern float for goto if inline int long register return short signed sizeof static struct switch typedef union unsigned void volatile while bool true false nullptr class public private protected template typename namespace using new delete virtual override std include define',
    java: 'abstract boolean break byte case catch char class continue default do double else enum extends final finally float for if implements import instanceof int interface long new null package private protected public return short static super switch this throw throws true false try void while var record',
    sql: 'select from where group by order having join inner left right outer on as insert into values update set delete create table primary key foreign references not null and or in is distinct limit offset union all exists case when then else end count sum avg min max',
    r: 'if else repeat while function for in next break TRUE FALSE NULL Inf NaN NA library return',
    sh: 'if then else elif fi for while do done case esac in function return export local echo cd exit',
    m: 'function end if else elseif for while switch case otherwise return break continue true false',
    hs: 'case class data deriving do else if import in infix instance let module newtype of then type where',
    rs: 'as break const continue crate else enum extern false fn for if impl in let loop match mod move mut pub ref return self Self static struct super trait true type unsafe use where while async await dyn'
  };
  var FAMILY = { python: 'py', py: 'py', javascript: 'js', js: 'js', typescript: 'js', ts: 'js', json: 'js', c: 'c', cpp: 'c', 'c++': 'c', h: 'c', csharp: 'java', cs: 'java', java: 'java', kotlin: 'java', go: 'c', sql: 'sql', r: 'r', bash: 'sh', sh: 'sh', shell: 'sh', matlab: 'm', octave: 'm', haskell: 'hs', rust: 'rs', rs: 'rs' };
  var LINE_COMMENT = { py: '#', r: '#', sh: '#', sql: '--', hs: '--', m: '%' };

  ALS.highlight = function (code, lang) {
    var fam = FAMILY[String(lang || '').toLowerCase()] || 'js';
    var kws = {};
    (KW[fam] || '').split(' ').forEach(function (k) { kws[fam === 'sql' ? k.toLowerCase() : k] = 1; });
    var lc = LINE_COMMENT[fam] || '//';
    var lines = String(code).replace(/\r\n?/g, '\n').replace(/\t/g, '    ').split('\n');
    var inBlock = false;
    return lines.map(function (line) {
      var out = '', i = 0;
      while (i < line.length) {
        if (inBlock) {
          var end = line.indexOf('*/', i);
          if (end < 0) { out += '<span class="tok-c">' + ALS.esc(line.slice(i)) + '</span>'; i = line.length; }
          else { out += '<span class="tok-c">' + ALS.esc(line.slice(i, end + 2)) + '</span>'; i = end + 2; inBlock = false; }
          continue;
        }
        var rest = line.slice(i);
        if (rest.indexOf(lc) === 0) { out += '<span class="tok-c">' + ALS.esc(rest) + '</span>'; break; }
        if (lc === '//' && rest.indexOf('/*') === 0) { inBlock = true; continue; }
        var m = rest.match(/^("(?:\\.|[^"\\])*"?|'(?:\\.|[^'\\])*'?|`(?:\\.|[^`\\])*`?)/);
        if (m) { out += '<span class="tok-s">' + ALS.esc(m[0]) + '</span>'; i += m[0].length; continue; }
        m = rest.match(/^\d+(?:\.\d+)?(?:e[+-]?\d+)?/i);
        if (m && !/[\w]/.test(line[i - 1] || '')) { out += '<span class="tok-n">' + m[0] + '</span>'; i += m[0].length; continue; }
        m = rest.match(/^[A-Za-z_][\w]*/);
        if (m) {
          var w = m[0], key = fam === 'sql' ? w.toLowerCase() : w;
          out += kws[key] ? '<span class="tok-k">' + w + '</span>' : ALS.esc(w);
          i += w.length; continue;
        }
        out += ALS.esc(line[i]); i++;
      }
      return out || ' ';
    });
  };

  /* ---------------- SVG sanitising (diagram slides) ---------------- */
  ALS.safeSvg = function (svgText) {
    try {
      var doc = new DOMParser().parseFromString(String(svgText), 'image/svg+xml');
      var svg = doc.documentElement;
      if (!svg || svg.nodeName.toLowerCase() !== 'svg' || doc.getElementsByTagName('parsererror').length) return null;
      var walk = function (n) {
        Array.prototype.slice.call(n.children || []).forEach(function (c) {
          var name = c.nodeName.toLowerCase();
          if (name === 'script' || name === 'foreignobject' || name === 'iframe') { c.remove(); return; }
          Array.prototype.slice.call(c.attributes).forEach(function (a) {
            var an = a.name.toLowerCase();
            if (an.indexOf('on') === 0) c.removeAttribute(a.name);
            if ((an === 'href' || an === 'xlink:href') && /^\s*javascript:/i.test(a.value)) c.removeAttribute(a.name);
          });
          walk(c);
        });
      };
      Array.prototype.slice.call(svg.attributes).forEach(function (a) { if (a.name.toLowerCase().indexOf('on') === 0) svg.removeAttribute(a.name); });
      walk(svg);
      return document.importNode(svg, true);
    } catch (e) { return null; }
  };

  /* ---------------- keyboard ---------------- */
  ALS.onKey = function (map) {
    document.addEventListener('keydown', function (e) {
      var t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)) return;
      if (t && t.tagName === 'BUTTON' && (e.key === 'Enter' || e.key === ' ')) return; // let the focused button act
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      var fn = map[e.key] || map[e.code];
      if (fn) { e.preventDefault(); fn(e); }
    });
  };

  /* ---------------- icons ---------------- */
  var P = {
    palette: '<circle cx="13.5" cy="6.5" r="1.2"/><circle cx="17.5" cy="10.5" r="1.2"/><circle cx="8.5" cy="7.5" r="1.2"/><circle cx="6.5" cy="12.5" r="1.2"/><path d="M12 2a10 10 0 0 0 0 20c1.1 0 2-.9 2-2 0-.5-.2-1-.5-1.3-.3-.4-.5-.8-.5-1.3 0-1.1.9-2 2-2h2.3A5.7 5.7 0 0 0 22 9.7C22 5.4 17.5 2 12 2z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    shuffle: '<path d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/>',
    download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
    print: '<path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
    left: '<path d="m15 18-6-6 6-6"/>',
    right: '<path d="m9 18 6-6-6-6"/>',
    grid: '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
    expand: '<path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/>',
    rotate: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8M3 3v5h5"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    bulb: '<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/>',
    eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    notes: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    play: '<path d="m6 4 14 8-14 8z"/>',
    pause: '<path d="M7 4h3v16H7zM14 4h3v16h-3z"/>'
  };
  ALS.icon = function (name) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (P[name] || '') + '</svg>';
  };
  ALS.iconBtn = function (name, label, onclick, extraClass) {
    return ALS.el('button', { type: 'button', class: 'als-btn als-btn--ghost als-iconbtn ' + (extraClass || ''), 'aria-label': label, title: label, html: ALS.icon(name), onclick: onclick });
  };

  /* ---------------- theme + mode ---------------- */
  var root = document.documentElement;
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  ALS.loadFonts = function (name) {
    var t = THEMES[name];
    if (!t || !t.fonts || ALS.$('link[data-als-fonts="' + name + '"]')) return;
    document.head.appendChild(ALS.el('link', { rel: 'stylesheet', href: t.fonts, 'data-als-fonts': name }));
  };

  ALS.setTheme = function (name, persist) {
    if (!THEMES[name]) name = root.getAttribute('data-als-default') || Object.keys(THEMES)[0];
    root.setAttribute('data-als-theme', name);
    ALS.loadFonts(name);
    if (persist) ALS.store.set('theme', name);
    ALS.$$('[data-theme-option]').forEach(function (b) { b.setAttribute('aria-checked', String(b.getAttribute('data-theme-option') === name)); });
  };

  ALS.applyMode = function () {
    var pref = ALS.store.globalGet('mode', 'auto');
    var dark = pref === 'dark' || (pref === 'auto' && media && media.matches);
    root.setAttribute('data-als-mode', dark ? 'dark' : 'light');
    var btn = ALS.$('#als-mode-btn');
    if (btn) {
      btn.innerHTML = ALS.icon(dark ? 'sun' : 'moon');
      btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      btn.title = btn.getAttribute('aria-label');
    }
  };
  if (media && media.addEventListener) media.addEventListener('change', ALS.applyMode);

  function themeMenu() {
    var wrap = ALS.el('div', { class: 'als-menu als-noprint' });
    var btn = ALS.iconBtn('palette', 'Choose design', function (e) {
      e.stopPropagation();
      wrap.setAttribute('data-open', wrap.getAttribute('data-open') === 'true' ? 'false' : 'true');
    });
    btn.setAttribute('aria-haspopup', 'menu');
    var panel = ALS.el('div', { class: 'als-menu-panel', role: 'menu' });
    Object.keys(THEMES).forEach(function (name) {
      var t = THEMES[name];
      var sw = ALS.el('span', { class: 'als-swatch', style: 'background: linear-gradient(135deg,' + t.swatch[0] + ' 50%,' + t.swatch[1] + ' 50%)' });
      var label = ALS.el('span', { html: ALS.esc(t.label) + '<small>' + ALS.esc(t.short || '') + '</small>' });
      panel.appendChild(ALS.el('button', {
        type: 'button', class: 'als-menu-item', role: 'menuitemradio', 'data-theme-option': name,
        onclick: function () { ALS.setTheme(name, true); wrap.setAttribute('data-open', 'false'); }
      }, [sw, label]));
    });
    document.addEventListener('click', function (e) { if (!wrap.contains(e.target)) wrap.setAttribute('data-open', 'false'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') wrap.setAttribute('data-open', 'false'); });
    wrap.appendChild(btn); wrap.appendChild(panel);
    return wrap;
  }

  /* Top bar: title, optional actions, theme menu and mode toggle. */
  ALS.topbar = function (actions) {
    var d = ALS.data;
    var bar = ALS.el('header', { class: 'als-topbar' });
    var shell = ALS.el('div', { class: 'als-shell' });
    var brand = ALS.el('div', { class: 'als-brand' }, [
      ALS.el('span', { class: 'als-brand-title', text: d.title }),
      d.subtitle || d.subject ? ALS.el('span', { class: 'als-brand-sub', text: d.subtitle || d.subject }) : null
    ]);
    shell.appendChild(brand);
    shell.appendChild(ALS.el('div', { class: 'als-spacer' }));
    (actions || []).forEach(function (a) { if (a) shell.appendChild(a); });
    shell.appendChild(themeMenu());
    var modeBtn = ALS.iconBtn('moon', 'Toggle dark mode', function () {
      var dark = root.getAttribute('data-als-mode') === 'dark';
      ALS.store.globalSet('mode', dark ? 'light' : 'dark');
      ALS.applyMode();
    }, 'als-noprint');
    modeBtn.id = 'als-mode-btn';
    shell.appendChild(modeBtn);
    bar.appendChild(shell);
    return bar;
  };

  /* Source + grounding badges for an item. */
  ALS.provenance = function (item) {
    if (!item) return null;
    var bits = [];
    if (item.src) bits.push('<span class="als-src" title="Source in your material">' + ALS.esc(item.src) + '</span>');
    if (item.grounded === false) bits.push('<span class="als-beyond" title="Added beyond your course material">beyond your notes</span>');
    if (!bits.length) return null;
    return ALS.el('div', { class: 'als-row als-provenance', html: bits.join(' ') });
  };

  /* Results export shared by the flashcards and trainer templates. */
  ALS.exportResults = function (kind, items, extra) {
    var d = ALS.data;
    var payload = Object.assign({
      als: '1', kind: 'results', source: kind, title: d.title, module: d.module || null,
      date: ALS.today(), exported: new Date().toISOString(), items: items
    }, extra || {});
    var name = (d.module ? d.module + '-' : '') + ALS.slug(d.title) + '-results-' + ALS.today() + '.json';
    ALS.download(name, JSON.stringify(payload, null, 2));
    ALS.toast('Saved ' + name + '. Ask Claude to import it to update your progress.');
  };

  /* ---------------- boot ---------------- */
  ALS.boot = function (render) {
    var node = document.getElementById('als-data');
    try { ALS.data = JSON.parse(node.textContent); }
    catch (e) {
      document.body.innerHTML = '<p style="padding:2rem;font-family:sans-serif">This page has no valid data block. Rebuild it with <code>als.py build</code>.</p>';
      return;
    }
    ALS.pageKey = ALS.slug((ALS.data.module || '') + '-' + ALS.data.kind + '-' + ALS.data.title);
    ALS.macros = Object.assign({}, ALS.data.macros || {}); // LaTeX shorthands defined once per data file
    ALS.setTheme(ALS.store.get('theme', root.getAttribute('data-als-theme')));
    ALS.applyMode();
    if (ALS.hasMath(node.textContent)) ALS.loadKatex();
    render(ALS.data);
    ALS.applyMode();
    ALS.renderMath(document);
  };
})();
