/* ALS core runtime, shared by every template and inlined at build time.
   Provides: data loading, i18n (ALS.t) and right-to-left support, theme + light/dark switching,
   safe Markdown-lite with KaTeX maths (including automatic typesetting of plain-text maths and numbers),
   code highlighting, SVG sanitising, storage, downloads, keyboard helpers, the top bar, collapsible
   panels and the status bar (panel toggles, study timer, focus countdown, clock, text zoom). */
(function () {
  'use strict';

  var ALS = (window.ALS = window.ALS || {});
  var THEMES = window.ALS_THEMES || {};
  var I18N = window.ALS_I18N || {};
  var KATEX = 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.11/';
  var RTL_LANGS = { ar: 1, he: 1, fa: 1, ur: 1, ps: 1, sd: 1, ckb: 1, yi: 1, dv: 1, ug: 1 };

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
    return String(s || '').toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9\u0600-\u06ff]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'item';
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
    ALS._toastTimer = setTimeout(function () { t.removeAttribute('data-show'); }, 2600);
  };

  ALS.clock = function (sec) {
    sec = Math.max(0, Math.round(sec));
    var h = Math.floor(sec / 3600), m = Math.floor(sec % 3600 / 60), s = sec % 60;
    return (h ? h + ':' + String(m).padStart(2, '0') : String(m)) + ':' + String(s).padStart(2, '0');
  };

  /* ---------------- i18n: English strings are the keys ---------------- */
  ALS.lang = 'en';
  ALS.rtl = false;
  ALS.t = function (s) {
    var d = I18N[ALS.lang];
    var out = (d && d[s]) || s;
    for (var i = 1; i < arguments.length; i++) out = out.split('{' + (i - 1) + '}').join(String(arguments[i]));
    return out;
  };
  var T = ALS.t;

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

  /* ---------------- maths: explicit delimiters ---------------- */
  // $$…$$ | \[…\] | \(…\) | $…$ | \begin{env}…\end{env} | $ padded maths $ (only when it clearly is maths)
  var MATH_RE = /\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$(?!\s)((?:\\\$|[^$\n])+?)(?<!\s)\$(?!\d)|(\\begin\{([a-zA-Z*]+)\}[\s\S]+?\\end\{\6\})|\$[ \t]+((?:[^$\n])*?[\\^_=+{<>](?:[^$\n])*?)[ \t]+\$/g;
  var MATHY = /[=^_]|[\u0370-\u03ff\u00b2\u00b3\u00b9\u2070-\u209f\u2190-\u21ff\u2200-\u22ff]/;

  ALS.hasMath = function (s) { s = String(s || ''); MATH_RE.lastIndex = 0; return MATH_RE.test(s) || MATHY.test(s); };

  /* A maths field ("math", "formula", "sym") may arrive wrapped in $…$ or \[…\]: strip the wrapper. */
  ALS.tex = function (s) {
    s = String(s == null ? '' : s).trim();
    var m = s.match(/^\$\$([\s\S]*)\$\$$/) || s.match(/^\\\[([\s\S]*)\\\]$/) || s.match(/^\\\(([\s\S]*)\\\)$/) || s.match(/^\$([^$]*)\$$/);
    return m ? m[1].trim() : s;
  };

  function mathSpan(tex, display) {
    return '<span class="als-math' + (display ? ' als-math-display' : '') + '" data-display="' + (display ? 1 : 0) +
      '" data-tex="' + ALS.esc(tex) + '">' + ALS.esc(tex) + '</span>';
  }

  /* ---------------- maths: automatic typesetting of plain-text maths ----------------
     Authors forget delimiters. Conservative rules turn obvious maths into TeX:
       1. a token with Unicode maths (σ(z), x₁, O(n²), ∂L/∂w, ≤) and no ordinary word in it
       2. a token with ^ or _ applied to a single symbol (x^2, a_n, 10^3)
       3. an equation of simple terms (x = 3, f(3) = 6, p < 0.05, 2 + 3 = 5)
     and, in any text that contains maths, 4. standalone numbers (so 0.5 matches the formula next to it). */
  var SUP = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁺': '+', '⁻': '-', 'ⁿ': 'n', 'ⁱ': 'i', 'ᵀ': 'T', 'ᵏ': 'k', 'ˣ': 'x' };
  var SUB = { '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9', '₊': '+', '₋': '-', 'ᵢ': 'i', 'ⱼ': 'j', 'ₖ': 'k', 'ₙ': 'n', 'ₘ': 'm', 'ₜ': 't', 'ₓ': 'x', 'ₐ': 'a', 'ₚ': 'p', 'ₛ': 's' };
  var SYM = {
    'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'δ': '\\delta', 'ε': '\\varepsilon', 'ζ': '\\zeta', 'η': '\\eta', 'θ': '\\theta', 'ι': '\\iota', 'κ': '\\kappa',
    'λ': '\\lambda', 'μ': '\\mu', 'ν': '\\nu', 'ξ': '\\xi', 'π': '\\pi', 'ρ': '\\rho', 'σ': '\\sigma', 'ς': '\\varsigma', 'τ': '\\tau', 'υ': '\\upsilon', 'φ': '\\varphi',
    'χ': '\\chi', 'ψ': '\\psi', 'ω': '\\omega', 'ϕ': '\\phi', 'ϵ': '\\epsilon', 'ϑ': '\\vartheta',
    'Γ': '\\Gamma', 'Δ': '\\Delta', 'Θ': '\\Theta', 'Λ': '\\Lambda', 'Ξ': '\\Xi', 'Π': '\\Pi', 'Σ': '\\Sigma', 'Φ': '\\Phi', 'Ψ': '\\Psi', 'Ω': '\\Omega',
    '×': '\\times', '·': '\\cdot', '⋅': '\\cdot', '÷': '\\div', '±': '\\pm', '∓': '\\mp', '≤': '\\le', '≥': '\\ge', '≠': '\\ne', '≈': '\\approx', '≡': '\\equiv', '∝': '\\propto',
    '→': '\\to', '←': '\\leftarrow', '↔': '\\leftrightarrow', '⇒': '\\Rightarrow', '⇐': '\\Leftarrow', '⇔': '\\Leftrightarrow', '↦': '\\mapsto',
    '∈': '\\in', '∉': '\\notin', '⊂': '\\subset', '⊆': '\\subseteq', '⊃': '\\supset', '∪': '\\cup', '∩': '\\cap', '∅': '\\emptyset', '∖': '\\setminus',
    '∞': '\\infty', '∑': '\\sum', '∏': '\\prod', '∫': '\\int', '∂': '\\partial', '∇': '\\nabla', '√': '\\surd', '∀': '\\forall', '∃': '\\exists', '¬': '\\neg', '∧': '\\land', '∨': '\\lor',
    'ℝ': '\\mathbb{R}', 'ℕ': '\\mathbb{N}', 'ℤ': '\\mathbb{Z}', 'ℚ': '\\mathbb{Q}', 'ℂ': '\\mathbb{C}', '−': '-', '∘': '\\circ', '⊤': '\\top', '⊥': '\\bot', '′': "'", '°': '^\\circ',
    '∥': '\\parallel', '≪': '\\ll', '≫': '\\gg', '⊕': '\\oplus', '⊗': '\\otimes', '†': '\\dagger', 'ℓ': '\\ell', 'ħ': '\\hbar', '∗': '*', '≜': '\\triangleq', '∼': '\\sim'
  };
  var ACCENT = { '\u0302': '\\hat', '\u0304': '\\bar', '\u0307': '\\dot', '\u20d7': '\\vec' };
  var FUNC_NAMES = 'sin|cos|tan|cot|sec|csc|log|ln|exp|max|min|arg|det|dim|ker|lim|sup|inf|gcd|mod|tanh|sinh|cosh|argmax|argmin|sgn|var|cov|tr|rank';
  var FUNCS = new RegExp('^(?:' + FUNC_NAMES + ')$');
  var UNI_RE = /[\u0370-\u03ff\u00b2\u00b3\u00b9\u2070-\u209f\u1d40-\u1d7f\u2190-\u21ff\u2200-\u22ff\u2100-\u214f×÷±·°′\u0302\u0304\u0307\u20d7]/;

  function uniToTex(tok) {
    var out = '', i = 0, chars = Array.from(tok.normalize('NFD'));
    function run(map) { var r = ''; while (i < chars.length && map[chars[i]] != null) r += map[chars[i++]]; return r; }
    while (i < chars.length) {
      var c = chars[i];
      if (SUP[c] != null) { out += '^{' + run(SUP) + '}'; continue; }
      if (SUB[c] != null) { out += '_{' + run(SUB) + '}'; continue; }
      if (ACCENT[chars[i + 1]]) { out += ACCENT[chars[i + 1]] + '{' + (SYM[c] || c) + '}'; i += 2; continue; }
      if (SYM[c]) { out += SYM[c] + (/[a-zA-Z]$/.test(SYM[c]) ? ' ' : ''); i++; continue; }
      if (c === '%') { out += '\\%'; i++; continue; }
      if (c === '*') { out += '\\cdot '; i++; continue; }
      out += c; i++;
    }
    out = out.normalize('NFC').replace(/<=/g, '\\le ').replace(/>=/g, '\\ge ').replace(/!=/g, '\\ne ')
      .replace(/\\surd\s*\(([^()]*)\)/g, '\\sqrt{$1}').replace(/(\d),(\d)/g, '$1{,}$2');
    // function names upright: sin, log, max …
    return out.replace(/[A-Za-z]{2,}/g, function (word, pos, all) {
      if (/\\[A-Za-z]*$/.test(all.slice(0, pos))) return word;
      return FUNCS.test(word) ? '\\operatorname{' + word + '}' : word;
    });
  }

  function wordy(tok) {
    // an ordinary word hides in the token: 3+ letters in a row that are not a function name, or 2+ Greek letters in a row
    if (/[\u0370-\u03ff]{2,}/.test(tok)) return true;
    var words = tok.match(/[A-Za-z\u00c0-\u024f]{3,}/g) || [];
    return words.some(function (w) { return !FUNCS.test(w); });
  }
  function balance(s, open, close) { return s.split(open).length - s.split(close).length; }

  var ATOM = "(?:\\d+(?:[.,]\\d+)?%?|\\d*[A-Za-z](?:'{1,2})?(?:[_^](?:\\{[^{}\\s]{1,8}\\}|[A-Za-z0-9]))*(?:\\([^()\\s]{0,14}\\))?)";
  var EXPR = '-?' + ATOM + '(?:\\s?[+\\-*/]\\s?' + ATOM + ')*';
  var EQ_RE = new RegExp('(^|[\\s(\\[,;:*])(' + EXPR + '(?:\\s?(?:<=|>=|!=|=|<|>)\\s?' + EXPR + ')+)(?=$|[\\s)\\],;:.!?*])', 'g');
  var POW_RE = /^\(?(?:\d+(?:\.\d+)?)?[A-Za-z]{0,2}(?:[_^](?:\{[^{}]{1,12}\}|-?\d{1,3}|[A-Za-z]))+\)?$/;
  var NUM_RE = /(^|[\s(\[=:,;*])(-?\d+(?:[.,]\d+)?%?)(?=$|[\s)\],;:.!?*])/g;
  var PEEL = /^([(\["'“‘]*)([\s\S]*?)([)\]"'”’.,;:!?]*)$/;
  var OP_TOK = /^(?:[+\-*\/=<>]|<=|>=|!=)$/;
  var NUM_TOK = /^-?\d+(?:[.,]\d+)?%?$/;
  var VAR_TOK = new RegExp('^-?' + ATOM + '$');
  var FN_TOK = new RegExp('^(?:' + FUNC_NAMES + ')\\([^()\\s]*\\)$');
  var CHEM = /^(?:[A-Z][a-z]?[\u2080-\u2089]*){1,6}$/;

  /* Split a token into leading punctuation, body and trailing punctuation, keeping balanced brackets in the body. */
  function peel(tok) {
    var m = tok.match(PEEL), pre = m[1], body = m[2], post = m[3];
    while (post && /^[)\]]/.test(post) && (post.charAt(0) === ')' ? balance(body, '(', ')') > 0 : balance(body, '[', ']') > 0)) { body += post.charAt(0); post = post.slice(1); }
    while (pre && /[(\[]$/.test(pre) && (pre.slice(-1) === '(' ? balance(body, ')', '(') > 0 : balance(body, ']', '[') > 0)) { body = pre.slice(-1) + body; pre = pre.slice(0, -1); }
    return { pre: pre, body: body, post: post };
  }
  /* M = unmistakable maths, O = operator, N = number, V = single symbol or call, C = chemical formula, X = ordinary text */
  function kind(body) {
    if (!body || /[\u0590-\u06ff]/.test(body)) return 'X';
    if (CHEM.test(body) && /[\u2080-\u2089]/.test(body)) return 'C';
    if ((UNI_RE.test(body.normalize('NFD')) && !wordy(body)) || POW_RE.test(body)) return 'M';
    if (OP_TOK.test(body)) return 'O';
    if (NUM_TOK.test(body)) return 'N';
    if (VAR_TOK.test(body) || FN_TOK.test(body)) return 'V';
    return 'X';
  }

  function autoMath(s, hold, hadMath) {
    var found = hadMath;
    function put(tex) { found = true; return hold(mathSpan(tex, false)); }
    // rules 1 and 2: the longest run of maths-like tokens around at least one unmistakable one
    var parts = s.split(/(\s+)/), out = [], i = 0;
    while (i < parts.length) {
      var tok = parts[i];
      if (i % 2 === 1 || !tok) { out.push(tok); i++; continue; }
      var j = i, kinds = [];
      while (j < parts.length) {
        var t = parts[j];
        if (!t || t.indexOf('\u0000') > -1 || t.indexOf('](') > -1 || /^https?:/.test(t)) break;
        var p = peel(t), k = kind(p.body || t.replace(/[.,;:!?]+$/, ''));
        if (k === 'X' || (k === 'C' && j > i)) break;
        kinds.push(k);
        j += 2;
        if (k === 'C' || /[.;:!?"'”’]/.test(p.post) || /\n/.test(parts[j - 1] || '')) break;
      }
      var n = kinds.length;
      while (n > 0 && kinds[n - 1] === 'O') n--;                    // no trailing operator
      var lead = kinds[0] === 'O' && !(tok === '-' && n > 1);       // no leading operator, except a minus sign
      if (!lead && n > 0 && kinds.slice(0, n).some(function (x) { return x === 'M' || x === 'C'; })) {
        var q = peel(parts.slice(i, i + 2 * n - 1).join(''));
        out.push(q.pre + put(kinds[0] === 'C' ? '\\mathrm{' + uniToTex(q.body) + '}' : uniToTex(q.body)) + q.post);
        i += 2 * n - 1;
      } else { out.push(tok); i++; }
    }
    s = out.join('');
    // rule 3: equations of simple terms
    s = s.replace(EQ_RE, function (all, lead2, eq) {
      if (/^[A-Za-z]\s?=\s?[A-Za-z]{2,}/.test(eq)) return all;
      return lead2 + put(uniToTex(eq));
    });
    // rule 4: numbers, only where the text already has maths
    if (found) {
      s = s.replace(/(^|\n)(\s*\d+[.)])(?=\s)/g, function (m, x, y) { return x + y.replace(/\d/g, function (d) { return String.fromCharCode(0xE000 + +d); }); }); // protect list markers
      s = s.replace(NUM_RE, function (all, lead3, num) {
        if (/^\d{4}$/.test(num) && +num >= 1000 && +num <= 2100) return all; // years
        return lead3 + put(num.replace('%', '\\%').replace(/,(?=\d)/, '{,}'));
      });
      s = s.replace(/[\uE000-\uE009]/g, function (c) { return String(c.charCodeAt(0) - 0xE000); });
    }
    return s;
  }
  ALS.autoMathOn = true;

  /* ---------------- Markdown-lite ---------------- */
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

  /* Render a rich-text string to safe HTML. opts.inline = no paragraph wrapping; opts.plain = no automatic maths. */
  ALS.md = function (text, opts) {
    opts = opts || {};
    if (text == null) return '';
    var store = [];
    var hold = function (html) { store.push(html); return '\u0000' + (store.length - 1) + '\u0000'; };
    var s = String(text).replace(/\r\n?/g, '\n').replace(/[\u0000\uE000-\uE009]/g, '');

    s = s.replace(/`([^`\n]+)`/g, function (_, c) { return hold('<code>' + ALS.esc(c) + '</code>'); });
    var nCode = store.length;
    s = s.replace(MATH_RE, function (m, d1, d2, i1, i2, env, envName, i3) {
      if (d1 != null) return hold(mathSpan(d1.trim(), true));
      if (d2 != null) return hold(mathSpan(d2.trim(), true));
      if (env != null) return hold(mathSpan(env.trim(), true));
      return hold(mathSpan((i1 != null ? i1 : i2 != null ? i2 : i3).trim(), false));
    });
    if (ALS.autoMathOn && !opts.plain) s = autoMath(s, hold, store.length > nCode);
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

  /* Plain text of a rich string (browser tab title, outlines, word counts). */
  ALS.plain = function (text) {
    return String(text == null ? '' : text).replace(/\$\$?|\*\*|`/g, '').replace(/\\[a-zA-Z]+\s?/g, ' ').replace(/[{}]/g, '').replace(/\s+/g, ' ').trim();
  };
  ALS.words = function (text) { var p = ALS.plain(text); return p ? p.split(/\s+/).length : 0; };

  /* Set rich HTML on an element and typeset its maths. */
  ALS.rich = function (node, text, opts) {
    node.innerHTML = ALS.md(text, opts);
    if (!opts || !opts.noClass) node.classList.add('als-rich');
    ALS.renderMath(node);
    return node;
  };

  ALS.renderMath = function (root) {
    var nodes = ALS.$$('.als-math:not([data-done])', root || document);
    if (nodes.length) {
      if (!window.katex) {
        nodes.forEach(function (n) { n.classList.add('als-math-raw'); });
        ALS.loadKatex();
      } else {
        nodes.forEach(function (n) {
          try {
            window.katex.render(n.getAttribute('data-tex'), n, { displayMode: n.getAttribute('data-display') === '1', throwOnError: false, strict: 'ignore', macros: ALS.macros });
            n.classList.remove('als-math-raw');
            n.setAttribute('data-done', '1');
          } catch (e) { n.classList.add('als-math-raw'); }
        });
      }
    }
    ALS.fitMath(root);
  };

  /* Display maths never scrolls: it is scaled down to the width it has (to half size at most). */
  ALS.fitMath = function (root) {
    ALS.$$('.als-math-display[data-done]', root || document).forEach(function (n) {
      n.style.fontSize = '';
      var avail = n.clientWidth, need = n.scrollWidth;
      if (avail > 0 && need > avail + 1) n.style.fontSize = Math.max(0.5, avail / need * 0.985).toFixed(3) + 'em';
    });
  };
  var fitTimer;
  window.addEventListener('resize', function () { clearTimeout(fitTimer); fitTimer = setTimeout(function () { ALS.fitMath(document); }, 150); });

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

  /* ---------------- SVG sanitising (diagram slides) ----------------
     allowHtml keeps <foreignObject>; only for drawings this toolkit generates itself, whose labels are escaped. */
  ALS.safeSvg = function (svgText, allowHtml) {
    try {
      var doc = new DOMParser().parseFromString(String(svgText), 'image/svg+xml');
      var svg = doc.documentElement;
      if (!svg || svg.nodeName.toLowerCase() !== 'svg' || doc.getElementsByTagName('parsererror').length) return null;
      var walk = function (n) {
        Array.prototype.slice.call(n.children || []).forEach(function (c) {
          var name = c.nodeName.toLowerCase();
          if (name === 'script' || name === 'iframe' || (name === 'foreignobject' && !allowHtml)) { c.remove(); return; }
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
    pause: '<path d="M7 4h3v16H7zM14 4h3v16h-3z"/>',
    panelTop: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/>',
    panelLeft: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/>',
    panelBottom: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 15h18"/>',
    zen: '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>',
    timer: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M9 2h6"/>',
    target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
    layers: '<path d="m12 2 9 5-9 5-9-5z"/><path d="m3 12 9 5 9-5M3 17l9 5 9-5"/>',
    down: '<path d="m6 9 6 6 6-6"/>',
    up: '<path d="m18 15-6-6-6 6"/>',
    minus: '<path d="M5 12h14"/>',
    plus: '<path d="M12 5v14M5 12h14"/>'
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
    if (!t) return;
    [['fonts', name], ['fontsRtl', name + '-rtl']].forEach(function (f) {
      if (!t[f[0]] || (f[0] === 'fontsRtl' && !ALS.rtl) || ALS.$('link[data-als-fonts="' + f[1] + '"]')) return;
      document.head.appendChild(ALS.el('link', { rel: 'stylesheet', href: t[f[0]], 'data-als-fonts': f[1] }));
    });
  };

  ALS.setTheme = function (name, persist) {
    if (!THEMES[name]) name = root.getAttribute('data-als-default') || Object.keys(THEMES)[0];
    root.setAttribute('data-als-theme', name);
    ALS.loadFonts(name);
    if (persist) ALS.store.set('theme', name);
    ALS.$$('[data-theme-option]').forEach(function (b) { b.setAttribute('aria-checked', String(b.getAttribute('data-theme-option') === name)); });
    setTimeout(function () { ALS.fitMath(document); }, 400);
  };

  ALS.applyMode = function () {
    var pref = ALS.store.globalGet('mode', 'auto');
    var dark = pref === 'dark' || (pref === 'auto' && media && media.matches);
    root.setAttribute('data-als-mode', dark ? 'dark' : 'light');
    var btn = ALS.$('#als-mode-btn');
    if (btn) {
      btn.innerHTML = ALS.icon(dark ? 'sun' : 'moon');
      btn.setAttribute('aria-label', dark ? T('Switch to light mode') : T('Switch to dark mode'));
      btn.title = btn.getAttribute('aria-label');
    }
  };
  if (media && media.addEventListener) media.addEventListener('change', ALS.applyMode);

  function themeMenu() {
    var wrap = ALS.el('div', { class: 'als-menu als-noprint' });
    var btn = ALS.iconBtn('palette', T('Choose design'), function (e) {
      e.stopPropagation();
      wrap.setAttribute('data-open', wrap.getAttribute('data-open') === 'true' ? 'false' : 'true');
    });
    btn.setAttribute('aria-haspopup', 'menu');
    var panel = ALS.el('div', { class: 'als-menu-panel', role: 'menu' });
    Object.keys(THEMES).forEach(function (name) {
      var t = THEMES[name];
      var sw = ALS.el('span', { class: 'als-swatch', style: 'background: linear-gradient(135deg,' + t.swatch[0] + ' 50%,' + t.swatch[1] + ' 50%)' });
      var label = ALS.el('span', { html: ALS.esc(t.label) + '<small>' + ALS.esc(T(t.short || '')) + '</small>' });
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

  /* ---------------- collapsible panels ----------------
     A panel is any element tagged with ALS.panel(id, node). Ids: header, sidebar, controls, status.
     Hidden panels are listed in <html data-als-hide="…"> and remembered per page kind. */
  ALS.panels = {};
  var PANEL_META = {
    header: ['panelTop', 'Header'], sidebar: ['panelLeft', 'Sidebar'], controls: ['panelBottom', 'Controls'], status: ['up', 'Status bar']
  };
  function hideKey() { return 'hide:' + ((ALS.data && ALS.data.kind) || 'page'); }
  function hiddenList() { return (root.getAttribute('data-als-hide') || '').split(' ').filter(Boolean); }
  function others() { return Object.keys(ALS.panels).filter(function (p) { return p !== 'status'; }); }
  function setHidden(list, persist) {
    root.setAttribute('data-als-hide', list.join(' '));
    if (persist !== false) ALS.store.globalSet(hideKey(), list.join(' '));
    ALS.$$('[data-panel-toggle]').forEach(function (b) { b.setAttribute('aria-pressed', String(list.indexOf(b.getAttribute('data-panel-toggle')) < 0)); });
    var z = ALS.$('#als-zen'); if (z) z.setAttribute('aria-pressed', String(ALS.isZen()));
    document.dispatchEvent(new Event('als:panels'));
    setTimeout(function () { ALS.fitMath(document); }, 60);
  }
  ALS.panel = function (id, node, label) {
    node.setAttribute('data-als-panel', id);
    ALS.panels[id] = label || T((PANEL_META[id] || [0, id])[1]);
    return node;
  };
  ALS.panelHidden = function (id) { return hiddenList().indexOf(id) > -1; };
  ALS.togglePanel = function (id, show) {
    var list = hiddenList(), at = list.indexOf(id);
    var want = show == null ? at > -1 : show;
    if (want && at > -1) list.splice(at, 1);
    if (!want && at < 0) list.push(id);
    setHidden(list);
  };
  ALS.isZen = function () {
    var list = hiddenList(), o = others();
    return o.length > 0 && o.every(function (p) { return list.indexOf(p) > -1; });
  };
  ALS.zen = function () {
    var o = others(), list = hiddenList();
    if (!o.length) return;
    if (ALS.isZen()) {
      var before = ALS._beforeZen || [];
      setHidden(list.filter(function (p) { return o.indexOf(p) < 0 || before.indexOf(p) > -1; }));
    } else {
      ALS._beforeZen = list;
      setHidden(list.filter(function (p) { return o.indexOf(p) < 0; }).concat(o));
      ALS.toast(T('Focus mode: press Z to bring the panels back'));
    }
  };

  /* Top bar: title, optional actions, theme menu and mode toggle. */
  ALS.topbar = function (actions) {
    var d = ALS.data;
    var bar = ALS.panel('header', ALS.el('header', { class: 'als-topbar' }));
    var shell = ALS.el('div', { class: 'als-shell' });
    var sub = d.subtitle || d.subject;
    var brand = ALS.el('div', { class: 'als-brand' }, [
      ALS.el('span', { class: 'als-brand-title', html: ALS.md(d.title, { inline: true }) }),
      sub ? ALS.el('span', { class: 'als-brand-sub', html: ALS.md(sub, { inline: true }) }) : null
    ]);
    shell.appendChild(brand);
    shell.appendChild(ALS.el('div', { class: 'als-spacer' }));
    (actions || []).forEach(function (a) { if (a) shell.appendChild(a); });
    shell.appendChild(themeMenu());
    var modeBtn = ALS.iconBtn('moon', T('Switch to dark mode'), function () {
      var dark = root.getAttribute('data-als-mode') === 'dark';
      ALS.store.globalSet('mode', dark ? 'light' : 'dark');
      ALS.applyMode();
    }, 'als-noprint');
    modeBtn.id = 'als-mode-btn';
    shell.appendChild(modeBtn);
    shell.appendChild(ALS.iconBtn('up', T('Hide: {0}', T('Header')), function () { ALS.togglePanel('header', false); }, 'als-noprint als-panel-close'));
    bar.appendChild(shell);
    return bar;
  };

  /* ---------------- status bar ----------------
     ALS.dock([controls…]) returns the bottom dock: optional controls above the status bar.
     ALS.status([{ k: 'Slide', v: '4 / 12' }, …]) fills the middle of the bar. */
  var timer = { sec: 0, total: 0, running: true, focusEnd: 0, focusLen: 25 * 60 };
  function seg(cls, title, kids, onclick) {
    return ALS.el(onclick ? 'button' : 'span', { class: 'als-seg-item ' + (cls || ''), title: title || null, type: onclick ? 'button' : null, onclick: onclick || null }, kids);
  }
  function ico(name) { return ALS.el('span', { class: 'i', html: ALS.icon(name) }); }
  ALS.status = function (items) {
    var box = ALS.$('#als-status-info'); if (!box) return;
    box.innerHTML = '';
    (items || []).forEach(function (it) {
      if (!it) return;
      box.appendChild(ALS.el('span', { class: 'als-seg-item' + (it.cls ? ' ' + it.cls : ''), title: it.title || null, html: (it.k ? '<span class="k">' + ALS.esc(it.k) + '</span> ' : '') + '<span class="v">' + ALS.esc(it.v) + '</span>' }));
    });
  };
  function paintTimer() {
    var a = ALS.$('#als-timer'), b = ALS.$('#als-focus'), c = ALS.$('#als-clock .v');
    if (a) {
      ALS.$('.v', a).textContent = ALS.clock(timer.sec);
      a.classList.toggle('is-paused', !timer.running);
      a.title = T('Study time on this page ({0} in total). Click to pause or resume.', ALS.clock(timer.total + timer.sec));
    }
    if (b) {
      var left = timer.focusEnd ? Math.max(0, Math.round((timer.focusEnd - Date.now()) / 1000)) : timer.focusLen;
      ALS.$('.v', b).textContent = ALS.clock(left);
      b.classList.toggle('is-on', !!timer.focusEnd);
    }
    if (c) { var d = new Date(); c.textContent = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); }
  }
  function tick() {
    if (!document.hidden && timer.running) { timer.sec++; if (timer.sec % 15 === 0) ALS.store.set('time', timer.total + timer.sec); }
    if (timer.focusEnd && Date.now() >= timer.focusEnd) {
      timer.focusEnd = 0;
      ALS.toast(T('Focus block finished. Take a short break.'));
      var f = ALS.$('#als-focus'); if (f) { f.classList.add('is-done'); setTimeout(function () { f.classList.remove('is-done'); }, 6000); }
    }
    paintTimer();
    document.dispatchEvent(new Event('als:tick'));
  }
  ALS.elapsed = function () { return timer.sec; };
  function applyZoom() {
    var z = parseFloat(ALS.store.globalGet('zoom', '100')) || 100;
    root.style.fontSize = z === 100 ? '' : z + '%';
    var v = ALS.$('#als-zoom-value'); if (v) v.textContent = z + '%';
    setTimeout(function () { ALS.fitMath(document); }, 60);
  }
  function setZoom(delta) {
    var z = delta === 0 ? 100 : Math.round((parseFloat(ALS.store.globalGet('zoom', '100')) || 100) + delta);
    ALS.store.globalSet('zoom', String(Math.max(70, Math.min(180, z))));
    applyZoom();
  }
  ALS.statusbar = function () {
    var bar = ALS.panel('status', ALS.el('div', { class: 'als-status als-noprint', role: 'toolbar', 'aria-label': T('Status bar') }));
    var left = ALS.el('div', { class: 'als-status-group' });
    others().forEach(function (id) {
      var label = T('Show or hide: {0}', ALS.panels[id]);
      var b = seg('als-seg-btn', label, [ico((PANEL_META[id] || ['panelTop'])[0])], function () { ALS.togglePanel(id); });
      b.setAttribute('data-panel-toggle', id);
      b.setAttribute('aria-label', label);
      left.appendChild(b);
    });
    var zen = seg('als-seg-btn', T('Focus mode: hide all panels (Z)'), [ico('zen')], ALS.zen);
    zen.id = 'als-zen'; zen.setAttribute('aria-label', T('Focus mode: hide all panels (Z)'));
    left.appendChild(zen);
    var info = ALS.el('div', { class: 'als-status-group als-status-info', id: 'als-status-info' });
    var right = ALS.el('div', { class: 'als-status-group als-status-end' });
    var t1 = seg('als-seg-btn', '', [ico('timer'), ALS.el('span', { class: 'v', text: '0:00' })], function () { timer.running = !timer.running; paintTimer(); });
    t1.id = 'als-timer';
    var t2 = seg('als-seg-btn', T('Focus countdown. Click to start or stop a 25-minute block; Shift+click for 50 minutes.'), [ico('target'), ALS.el('span', { class: 'v', text: '25:00' })], function (e) {
      if (timer.focusEnd) timer.focusEnd = 0;
      else { timer.focusLen = (e && e.shiftKey ? 50 : 25) * 60; timer.focusEnd = Date.now() + timer.focusLen * 1000; ALS.toast(T('Focus block started: {0} minutes', timer.focusLen / 60)); }
      paintTimer();
    });
    t2.id = 'als-focus';
    var clock = seg('als-hide-sm', T('Time'), [ALS.el('span', { class: 'v', text: '' })]); clock.id = 'als-clock';
    var zv = ALS.el('span', { class: 'v', id: 'als-zoom-value', text: '100%' });
    var zoom = ALS.el('span', { class: 'als-seg-group als-hide-sm' }, [
      seg('als-seg-btn', T('Smaller text'), [ico('minus')], function () { setZoom(-10); }),
      seg('als-seg-btn', T('Reset text size'), [zv], function () { setZoom(0); }),
      seg('als-seg-btn', T('Larger text'), [ico('plus')], function () { setZoom(10); })
    ]);
    var hide = seg('als-seg-btn', T('Hide: {0}', T('Status bar')) + ' (B)', [ico('down')], function () { ALS.togglePanel('status', false); });
    hide.setAttribute('aria-label', T('Hide: {0}', T('Status bar')));
    [t1, t2, clock, zoom, hide].forEach(function (n) { right.appendChild(n); });
    bar.appendChild(left); bar.appendChild(info); bar.appendChild(right);
    return bar;
  };
  ALS.dock = function (controls) {
    var dock = ALS.el('div', { class: 'als-dock als-noprint' });
    (controls || []).forEach(function (c) { if (c) dock.appendChild(c); });
    dock.appendChild(ALS.statusbar());
    var old = ALS.$('.als-handles'); if (old) old.remove();
    var handles = ALS.el('div', { class: 'als-handles als-noprint' });
    Object.keys(ALS.panels).forEach(function (id) {
      var label = T('Show: {0}', ALS.panels[id]);
      handles.appendChild(ALS.el('button', { type: 'button', class: 'als-handle', 'data-handle': id, title: label, 'aria-label': label, html: ALS.icon((PANEL_META[id] || ['panelTop'])[0]), onclick: function () { ALS.togglePanel(id, true); } }));
    });
    document.body.appendChild(handles);
    setTimeout(function () { setHidden(hiddenList(), false); applyZoom(); paintTimer(); }, 0);
    if (!ALS._ticking) ALS._ticking = setInterval(tick, 1000);
    return dock;
  };

  /* Source + grounding badges for an item. */
  ALS.provenance = function (item) {
    if (!item) return null;
    var bits = [];
    if (item.src) bits.push('<span class="als-src" title="' + ALS.esc(T('Source in your material')) + '">' + ALS.esc(item.src) + '</span>');
    if (item.grounded === false) bits.push('<span class="als-beyond" title="' + ALS.esc(T('Added beyond your course material')) + '">' + ALS.esc(T('beyond your notes')) + '</span>');
    if (!bits.length) return null;
    return ALS.el('div', { class: 'als-row als-provenance', html: bits.join(' ') });
  };

  /* Results export shared by the flashcards and trainer templates. */
  ALS.exportResults = function (kind, items, extra) {
    var d = ALS.data;
    var payload = Object.assign({
      als: '1', kind: 'results', source: kind, title: d.title, module: d.module || null,
      date: ALS.today(), exported: new Date().toISOString(), studySeconds: timer.sec, items: items
    }, extra || {});
    var name = (d.module ? d.module + '-' : '') + ALS.slug(d.title) + '-results-' + ALS.today() + '.json';
    ALS.download(name, JSON.stringify(payload, null, 2));
    ALS.toast(T('Saved {0}. Ask Claude to import it to update your progress.', name));
  };

  /* ---------------- boot ---------------- */
  ALS.boot = function (render) {
    var node = document.getElementById('als-data');
    try { ALS.data = JSON.parse(node.textContent); }
    catch (e) {
      document.body.innerHTML = '<p style="padding:2rem;font-family:sans-serif">This page has no valid data block. Rebuild it with <code>als.py build</code>.</p>';
      return;
    }
    var d = ALS.data;
    ALS.pageKey = ALS.slug((d.module || '') + '-' + d.kind + '-' + d.title);
    ALS.macros = Object.assign({}, d.macros || {}); // LaTeX shorthands defined once per data file
    ALS.autoMathOn = d.autoMath !== false;
    var code = String(d.lang || root.getAttribute('lang') || 'en').toLowerCase();
    ALS.lang = I18N[code] ? code : code.split('-')[0];
    ALS.rtl = d.dir ? d.dir === 'rtl' : !!RTL_LANGS[code.split('-')[0]];
    root.setAttribute('dir', ALS.rtl ? 'rtl' : 'ltr');
    document.title = ALS.plain(d.title);
    var stored = ALS.store.globalGet(hideKey(), null);
    root.setAttribute('data-als-hide', stored != null ? stored : (window.innerWidth < 1000 ? 'sidebar' : ''));
    timer.total = ALS.store.get('time', 0) || 0;
    ALS.setTheme(ALS.store.get('theme', root.getAttribute('data-als-theme')));
    ALS.applyMode();
    if (ALS.hasMath(node.textContent)) ALS.loadKatex();
    ALS.onKey({ 'z': ALS.zen, 'Z': ALS.zen, 'b': function () { ALS.togglePanel('status'); }, 'B': function () { ALS.togglePanel('status'); } });
    window.addEventListener('beforeunload', function () { ALS.store.set('time', timer.total + timer.sec); });
    render(d);
    ALS.applyMode();
    ALS.renderMath(document);
  };
})();
