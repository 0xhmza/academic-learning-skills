/* ALS visual components: compact specs in, themed SVG out.
   Each ALS.viz.<name>(spec) returns { svg: '<svg …>', auto: [[ids per step]] }.
   Ids are stable and documented in skills/visual-lesson/references/components.md;
   shared/scripts/als_lib/viz_ids.py mirrors them for validation. Keep both in sync. */
(function () {
  'use strict';
  var ALS = (window.ALS = window.ALS || {});
  var V = (ALS.viz = {});
  var esc = ALS.esc;
  var STYLES = { accent: 1, accent2: 1, good: 1, bad: 1, muted: 1, line: 1 };
  var CYCLE = ['accent', 'accent2', 'good', 'bad', 'line'];

  function r1(n) { return Math.round(n * 10) / 10; }
  function sty(s, fallback) { return STYLES[s] ? s : (fallback || 'accent'); }
  function strokeCls(s, fb) { return 'd-' + sty(s, fb); }
  function solidCls(s, fb) { return 'd-solid-' + sty(s, fb); }
  function textW(s, px) { return String(s == null ? '' : s).length * (px || 7.6); }
  function svgOpen(w, h) { return '<svg viewBox="0 0 ' + r1(w) + ' ' + r1(h) + '" xmlns="http://www.w3.org/2000/svg">'; }
  function text(x, y, s, cls, anchor, extra) {
    return '<text class="' + (cls || 'd-text') + '" x="' + r1(x) + '" y="' + r1(y) + '" text-anchor="' + (anchor || 'middle') + '"' + (extra || '') + '>' + esc(s) + '</text>';
  }
  function group(id, body, cls) { return '<g id="' + esc(id) + '"' + (cls ? ' class="' + cls + '"' : '') + '>' + body + '</g>'; }

  /* ---------------- safe expression compiler: "1/(1+exp(-x))" -> f(x) ---------------- */
  var FN = {
    exp: Math.exp, log: Math.log, ln: Math.log, log2: Math.log2, log10: Math.log10, sin: Math.sin, cos: Math.cos, tan: Math.tan,
    tanh: Math.tanh, sqrt: Math.sqrt, abs: Math.abs, sign: Math.sign, floor: Math.floor, ceil: Math.ceil, max: Math.max, min: Math.min, pow: Math.pow,
    sigmoid: function (x) { return 1 / (1 + Math.exp(-x)); },
    relu: function (x) { return Math.max(0, x); },
    step: function (x) { return x >= 0 ? 1 : 0; }
  };
  var CONST = { pi: Math.PI, e: Math.E };
  V.functions = Object.keys(FN);

  V.compile = function (src) {
    var clean = String(src).replace(/\s+/g, '');
    var t = clean.match(/\d+\.?\d*(?:e[+-]?\d+)?|\.\d+|[A-Za-z_]\w*|[-+*\/^(),]/gi) || [];
    if (t.join('') !== clean || !t.length) throw new Error('cannot read expression: ' + src);
    var i = 0;
    function expr() {
      var a = term();
      while (t[i] === '+' || t[i] === '-') { a = bin(t[i++], a, term()); }
      return a;
    }
    function term() {
      var a = unary();
      while (t[i] === '*' || t[i] === '/') { a = bin(t[i++], a, unary()); }
      return a;
    }
    function bin(op, a, b) {
      if (op === '+') return function (x) { return a(x) + b(x); };
      if (op === '-') return function (x) { return a(x) - b(x); };
      if (op === '*') return function (x) { return a(x) * b(x); };
      return function (x) { return a(x) / b(x); };
    }
    function unary() {
      if (t[i] === '-') { i++; var a = unary(); return function (x) { return -a(x); }; }
      if (t[i] === '+') { i++; return unary(); }
      return power();
    }
    function power() {
      var a = atom();
      if (t[i] === '^') { i++; var b = unary(); return function (x) { return Math.pow(a(x), b(x)); }; }
      return a;
    }
    function atom() {
      var tok = t[i++];
      if (tok == null) throw new Error('unexpected end of expression');
      if (tok === '(') { var e = expr(); if (t[i++] !== ')') throw new Error('missing )'); return e; }
      if (/^[\d.]/.test(tok)) { var n = parseFloat(tok); return function () { return n; }; }
      if (/^[A-Za-z_]/.test(tok)) {
        if (t[i] === '(') {
          i++;
          var fn = FN[tok.toLowerCase()], args = [];
          if (!fn) throw new Error('unknown function ' + tok);
          if (t[i] !== ')') { args.push(expr()); while (t[i] === ',') { i++; args.push(expr()); } }
          if (t[i++] !== ')') throw new Error('missing )');
          return function (x) { return fn.apply(null, args.map(function (a) { return a(x); })); };
        }
        if (tok === 'x') return function (x) { return x; };
        if (CONST[tok.toLowerCase()] != null) { var c = CONST[tok.toLowerCase()]; return function () { return c; }; }
        throw new Error('unknown name ' + tok);
      }
      throw new Error('unexpected ' + tok);
    }
    var f = expr();
    if (i < t.length) throw new Error('unexpected ' + t[i]);
    return f;
  };

  function niceTicks(lo, hi, n) {
    var span = hi - lo, raw = span / Math.max(1, n || 5);
    var mag = Math.pow(10, Math.floor(Math.log10(raw))), norm = raw / mag;
    var stepSize = (norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10) * mag;
    var out = [], v = Math.ceil(lo / stepSize - 1e-9) * stepSize;
    for (; v <= hi + 1e-9; v += stepSize) out.push(Math.abs(v) < 1e-12 ? 0 : +v.toPrecision(12));
    return out;
  }
  function fmt(v) { return String(+(+v).toPrecision(6)); }

  /* ---------------- plot: function curves, data series, points, guide lines ---------------- */
  var clipN = 0;
  V.plot = function (s) {
    var W = 640, H = 360, L = 58, R = 22, T = 20, B = 46;
    var xr = s.x || [-5, 5], yr = s.y || [-1, 1];
    var sx = function (x) { return L + (x - xr[0]) / (xr[1] - xr[0]) * (W - L - R); };
    var sy = function (y) { return H - B - (y - yr[0]) / (yr[1] - yr[0]) * (H - T - B); };
    var x0 = xr[0] <= 0 && xr[1] >= 0 ? sx(0) : L, y0 = yr[0] <= 0 && yr[1] >= 0 ? sy(0) : H - B;
    var tx = (s.ticks && s.ticks.x) || niceTicks(xr[0], xr[1], 6), ty = (s.ticks && s.ticks.y) || niceTicks(yr[0], yr[1], 5);
    var clip = 'als-clip-' + (++clipN);
    var out = svgOpen(W, H) + '<defs><clipPath id="' + clip + '"><rect x="' + L + '" y="' + T + '" width="' + (W - L - R) + '" height="' + (H - T - B) + '"/></clipPath></defs>';
    var auto = [['axes']];

    var ax = '';
    if (s.grid) {
      tx.forEach(function (v) { ax += '<line class="d-muted" stroke-width="1" opacity=".35" x1="' + r1(sx(v)) + '" y1="' + T + '" x2="' + r1(sx(v)) + '" y2="' + (H - B) + '"/>'; });
      ty.forEach(function (v) { ax += '<line class="d-muted" stroke-width="1" opacity=".35" x1="' + L + '" y1="' + r1(sy(v)) + '" x2="' + (W - R) + '" y2="' + r1(sy(v)) + '"/>'; });
    }
    ax += '<line class="d-line" stroke-width="1.5" x1="' + L + '" y1="' + r1(y0) + '" x2="' + (W - R) + '" y2="' + r1(y0) + '"/>';
    ax += '<line class="d-line" stroke-width="1.5" x1="' + r1(x0) + '" y1="' + T + '" x2="' + r1(x0) + '" y2="' + (H - B) + '"/>';
    tx.forEach(function (v) {
      ax += '<line class="d-line" stroke-width="1" x1="' + r1(sx(v)) + '" y1="' + r1(y0) + '" x2="' + r1(sx(v)) + '" y2="' + r1(y0 + 5) + '"/>';
      if (!(v === 0 && x0 !== L)) ax += text(sx(v), y0 + 19, fmt(v), 'd-text-muted');
    });
    ty.forEach(function (v) {
      ax += '<line class="d-line" stroke-width="1" x1="' + r1(x0 - 5) + '" y1="' + r1(sy(v)) + '" x2="' + r1(x0) + '" y2="' + r1(sy(v)) + '"/>';
      if (!(v === 0 && y0 !== H - B)) ax += text(x0 - 9, sy(v) + 4, fmt(v), 'd-text-muted', 'end');
    });
    if (s.xlabel) ax += text(W - R, H - 8, s.xlabel, 'd-text-muted', 'end');
    if (s.ylabel) ax += text(L - 44, T - 4, s.ylabel, 'd-text-muted', 'start');
    out += group('axes', ax);

    var legendY = T + 14, legendN = 0;
    function legend(label, style, dash) {
      if (!label) return '';
      var lx = s.legend === 'left' ? L + 14 : W - R - 14 - textW(label) - 30, y = legendY + legendN * 20;
      legendN++;
      return '<line class="' + strokeCls(style) + '" stroke-width="3"' + (dash ? ' stroke-dasharray="6 4"' : '') + ' x1="' + r1(lx) + '" y1="' + (y - 4) + '" x2="' + r1(lx + 22) + '" y2="' + (y - 4) + '"/>' +
        text(lx + 30, y, label, 'd-text d-halo', 'start');
    }

    (s.curves || []).forEach(function (c, k) {
      var id = c.id || 'c' + (k + 1), style = c.style || CYCLE[k % CYCLE.length], d = '', pen = false, pts = [];
      if (c.data) pts = c.data;
      else {
        var f; try { f = V.compile(c.fn); } catch (e) { f = function () { return NaN; }; }
        var a = c.from != null ? c.from : xr[0], b = c.to != null ? c.to : xr[1], N = 240;
        for (var j = 0; j <= N; j++) { var xv = a + (b - a) * j / N; pts.push([xv, f(xv)]); }
      }
      var pad = (yr[1] - yr[0]) * 3;
      pts.forEach(function (p) {
        var ok = isFinite(p[1]) && p[1] > yr[0] - pad && p[1] < yr[1] + pad;
        if (!ok) { pen = false; return; }
        d += (pen ? 'L' : 'M') + r1(sx(p[0])) + ' ' + r1(sy(p[1])) + ' ';
        pen = true;
      });
      var body = '<path class="' + strokeCls(style) + ' ls-draw" stroke-width="3" stroke-linejoin="round" clip-path="url(#' + clip + ')"' + (c.dash ? ' stroke-dasharray="7 5"' : '') + ' d="' + d.trim() + '"/>' + legend(c.label, style, c.dash);
      out += group(id, body);
      auto.push([id]);
    });

    (s.scatter || []).forEach(function (sc, k) {
      var id = sc.id || 's' + (k + 1), style = sc.style || CYCLE[k % CYCLE.length], body = '';
      (sc.data || []).forEach(function (p) {
        var px = sx(p[0]), py = sy(p[1]);
        if (sc.shape === 'x') body += '<path class="' + strokeCls(style) + '" stroke-width="2.5" d="M' + r1(px - 4.5) + ' ' + r1(py - 4.5) + 'l9 9M' + r1(px + 4.5) + ' ' + r1(py - 4.5) + 'l-9 9"/>';
        else body += '<circle class="' + solidCls(style) + '" cx="' + r1(px) + '" cy="' + r1(py) + '" r="4.5"/>';
      });
      if (sc.label) {
        var lx = s.legend === 'left' ? L + 14 : W - R - 14 - textW(sc.label) - 30, y = legendY + legendN * 20; legendN++;
        body += (sc.shape === 'x' ? '<path class="' + strokeCls(style) + '" stroke-width="2.5" d="M' + r1(lx + 6) + ' ' + (y - 9) + 'l9 9M' + r1(lx + 15) + ' ' + (y - 9) + 'l-9 9"/>' : '<circle class="' + solidCls(style) + '" cx="' + r1(lx + 11) + '" cy="' + (y - 4) + '" r="4.5"/>') + text(lx + 30, y, sc.label, 'd-text d-halo', 'start');
      }
      out += group(id, body);
      auto.push([id]);
    });

    var last = [];
    (s.lines || []).forEach(function (ln, k) {
      var id = ln.id || 'l' + (k + 1), style = ln.style || 'muted', body;
      if (ln.x != null) {
        body = '<line class="' + strokeCls(style, 'muted') + '" stroke-width="1.5" stroke-dasharray="6 4" x1="' + r1(sx(ln.x)) + '" y1="' + T + '" x2="' + r1(sx(ln.x)) + '" y2="' + (H - B) + '"/>' +
          (ln.label ? text(sx(ln.x) + 6, T + 12, ln.label, 'd-text-muted d-halo', 'start') : '');
      } else {
        body = '<line class="' + strokeCls(style, 'muted') + '" stroke-width="1.5" stroke-dasharray="6 4" x1="' + L + '" y1="' + r1(sy(ln.y)) + '" x2="' + (W - R) + '" y2="' + r1(sy(ln.y)) + '"/>' +
          (ln.label ? text(L + 8, sy(ln.y) - 6, ln.label, 'd-text-muted d-halo', 'start') : '');
      }
      out += group(id, body); last.push(id);
    });
    (s.points || []).forEach(function (p, k) {
      var id = p.id || 'p' + (k + 1), px = sx(p.at[0]), py = sy(p.at[1]), left = px > W - R - 110;
      var body = '<circle class="' + solidCls(p.style) + '" cx="' + r1(px) + '" cy="' + r1(py) + '" r="5"/>' +
        (p.label ? text(px + (left ? -9 : 9), py - 9, p.label, 'd-text-accent d-halo', left ? 'end' : 'start') : '');
      out += group(id, body); last.push(id);
    });
    (s.notes || []).forEach(function (n, k) {
      var id = n.id || 't' + (k + 1);
      out += group(id, text(sx(n.at[0]), sy(n.at[1]), n.text, 'd-text d-halo', n.anchor || 'start')); last.push(id);
    });
    if (last.length) auto.push(last);
    return { svg: out + '</svg>', auto: auto };
  };

  /* ---------------- flow: boxes and arrows with automatic layout ---------------- */
  function parseNode(n) {
    if (typeof n === 'string') { var k = n.indexOf(':'); return k < 0 ? { id: n.trim(), label: n.trim() } : { id: n.slice(0, k).trim(), label: n.slice(k + 1).trim() }; }
    return n;
  }
  function parseEdges(list) {
    var out = [];
    (list || []).forEach(function (e) {
      if (typeof e === 'string') {
        var k = e.indexOf(':'), label = k < 0 ? '' : e.slice(k + 1).trim(), chain = (k < 0 ? e : e.slice(0, k)).split('>').map(function (x) { return x.trim(); });
        for (var j = 0; j + 1 < chain.length; j++) out.push({ from: chain[j], to: chain[j + 1], label: j === chain.length - 2 ? label : '' });
      } else if (Array.isArray(e)) out.push({ from: e[0], to: e[1], label: e[2] || '' });
      else out.push(e);
    });
    return out;
  }
  V.parseNode = parseNode; V.parseEdges = parseEdges;

  function clipToBox(cx, cy, hw, hh, tx, ty, shape) {
    var dx = tx - cx, dy = ty - cy;
    if (!dx && !dy) return [cx, cy];
    if (shape === 'circle') { var len = Math.sqrt(dx * dx + dy * dy); return [cx + dx / len * hw, cy + dy / len * hw]; }
    var k = Math.min(dx ? hw / Math.abs(dx) : Infinity, dy ? hh / Math.abs(dy) : Infinity);
    return [cx + dx * k, cy + dy * k];
  }
  function nodeBox(n) {
    var shape = n.shape || 'box';
    if (shape === 'circle') { var rad = Math.max(24, Math.max(textW(n.label), textW(n.sub, 6.4)) / 2 + 10); return { w: rad * 2, h: rad * 2 }; }
    return { w: Math.max(88, Math.max(textW(n.label), textW(n.sub, 6.4)) + 28), h: n.sub ? 58 : 44 };
  }
  function drawNode(n, cx, cy, b) {
    var cls = n.style === 'accent' ? 'd-fill-accent' : 'd-fill', shape = n.shape || 'box', body;
    if (shape === 'circle') body = '<circle class="' + cls + '" stroke-width="1.5" cx="' + r1(cx) + '" cy="' + r1(cy) + '" r="' + r1(b.w / 2) + '"/>';
    else body = '<rect class="' + cls + '" stroke-width="1.5" x="' + r1(cx - b.w / 2) + '" y="' + r1(cy - b.h / 2) + '" width="' + r1(b.w) + '" height="' + r1(b.h) + '" rx="' + (shape === 'pill' ? r1(b.h / 2) : 8) + '"/>';
    body += text(cx, cy + (n.sub ? -3 : 5), n.label, n.style === 'accent' ? 'd-text-accent' : 'd-text');
    if (n.sub) body += text(cx, cy + 15, n.sub, 'd-text-muted');
    return body;
  }
  function arrow(x1, y1, x2, y2, style, label, curve) {
    var cls = strokeCls(style, 'line'), mk = 'als-arrow' + (style && STYLES[style] && style !== 'line' ? '-' + style : '');
    var body, mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    if (curve) {
      var dx = x2 - x1, dy = y2 - y1, len = Math.sqrt(dx * dx + dy * dy) || 1, qx = mx - dy / len * curve, qy = my + dx / len * curve;
      body = '<path class="' + cls + ' ls-draw" stroke-width="1.8" marker-end="url(#' + mk + ')" d="M' + r1(x1) + ' ' + r1(y1) + ' Q' + r1(qx) + ' ' + r1(qy) + ' ' + r1(x2) + ' ' + r1(y2) + '"/>';
      mx = (mx + qx) / 2; my = (my + qy) / 2;
    } else body = '<line class="' + cls + ' ls-draw" stroke-width="1.8" marker-end="url(#' + mk + ')" x1="' + r1(x1) + '" y1="' + r1(y1) + '" x2="' + r1(x2) + '" y2="' + r1(y2) + '"/>';
    if (label) body += text(mx, my - 6, label, 'd-text-muted d-halo');
    return body;
  }

  V.flow = function (s) {
    var nodes = (s.nodes || []).map(parseNode), edges = parseEdges(s.edges), byId = {}, down = s.dir === 'down';
    nodes.forEach(function (n) { byId[n.id] = n; n._b = nodeBox(n); });
    edges = edges.filter(function (e) { return byId[e.from] && byId[e.to]; });
    // back edges (cycles) are found by depth-first search and left out of the layering
    var state = {}, outs = {};
    nodes.forEach(function (n) { outs[n.id] = []; });
    edges.forEach(function (e) { outs[e.from].push(e); });
    (function () {
      function visit(id) { state[id] = 1; outs[id].forEach(function (e) { if (state[e.to] === 1) e.back = true; else if (!state[e.to]) visit(e.to); }); state[id] = 2; }
      nodes.forEach(function (n) { if (!state[n.id]) visit(n.id); });
    })();
    var layer = {};
    nodes.forEach(function (n) { layer[n.id] = 0; });
    for (var pass = 0; pass < nodes.length; pass++) {
      var moved = false;
      edges.forEach(function (e) { if (!e.back && e.from !== e.to && layer[e.to] < layer[e.from] + 1) { layer[e.to] = layer[e.from] + 1; moved = true; } });
      if (!moved) break;
    }
    var cols = [];
    nodes.forEach(function (n) {
      if (n.at) { layer[n.id] = n.at[0]; }
      (cols[layer[n.id]] = cols[layer[n.id]] || []).push(n);
    });
    for (var c = 0; c < cols.length; c++) cols[c] = cols[c] || [];
    cols.forEach(function (col) { col.sort(function (a, b) { return (a.at ? a.at[1] : 1e6) - (b.at ? b.at[1] : 1e6); }); });
    var maxW = 0, maxH = 0, maxN = 0;
    nodes.forEach(function (n) { maxW = Math.max(maxW, n._b.w); maxH = Math.max(maxH, n._b.h); });
    cols.forEach(function (col) { maxN = Math.max(maxN, col.length); });
    var hasLabels = edges.some(function (e) { return e.label; });
    var gapMain = down ? 46 : (hasLabels ? 78 : 56), gapCross = down ? 28 : 22, pad = 18;
    var cellMain = (down ? maxH : maxW) + gapMain, cellCross = (down ? maxW : maxH) + gapCross;
    var mainLen = cols.length * cellMain - gapMain + pad * 2, crossLen = maxN * cellCross - gapCross + pad * 2;
    cols.forEach(function (col, ci) {
      col.forEach(function (n, ri) {
        var m = pad + ci * cellMain + (down ? maxH : maxW) / 2;
        var x = pad + (crossLen - pad * 2 - (col.length * cellCross - gapCross)) / 2 + ri * cellCross + (down ? maxW : maxH) / 2;
        n._x = down ? x : m; n._y = down ? m : x;
      });
    });
    var W = down ? crossLen : mainLen, H = down ? mainLen : crossLen, out = svgOpen(W, H), order = [];
    var pairSeen = {};
    edges.forEach(function (e) {
      var a = byId[e.from], b = byId[e.to], rev = e.to + '>' + e.from;
      var curve = e.back || pairSeen[rev] ? 34 : 0;
      pairSeen[e.from + '>' + e.to] = 1;
      var p1 = clipToBox(a._x, a._y, a._b.w / 2, a._b.h / 2, b._x, b._y, a.shape), p2 = clipToBox(b._x, b._y, b._b.w / 2 + 3, b._b.h / 2 + 3, a._x, a._y, b.shape);
      e._svg = group(e.from + '>' + e.to, arrow(p1[0], p1[1], p2[0], p2[1], e.style, e.label, curve));
    });
    edges.forEach(function (e) { out += e._svg; });
    var shown = {}, auto = [];
    cols.forEach(function (col) {
      col.forEach(function (n) {
        out += group(n.id, drawNode(n, n._x, n._y, n._b));
        shown[n.id] = 1;
        var st = [n.id];
        edges.forEach(function (e) { if (!e._done && shown[e.from] && shown[e.to]) { st.push(e.from + '>' + e.to); e._done = 1; } });
        auto.push(st);
      });
    });
    return { svg: out + '</svg>', auto: auto };
  };

  /* ---------------- tree ---------------- */
  V.treeNodes = function (root) {
    var list = [], n = 0;
    (function walk(t, parent, depth) {
      var node;
      if (typeof t === 'string') node = { label: t, kids: [] };
      else if (Array.isArray(t)) node = { label: String(t[0]), kids: t.slice(1) };
      else node = { label: t.label, id: t.id, style: t.style, sub: t.sub, kids: t.children || [] };
      n++; node.id = node.id || 'n' + n; node.parent = parent; node.depth = depth; node.children = [];
      list.push(node);
      if (parent) parent.children.push(node);
      node.kids.forEach(function (k) { walk(k, node, depth + 1); });
    })(root, null, 0);
    return list;
  };
  V.tree = function (s) {
    var list = V.treeNodes(s.root), slot = 0, maxD = 0, maxW = 0;
    list.forEach(function (n) { n._b = nodeBox({ label: n.label, sub: n.sub, shape: s.shape }); maxW = Math.max(maxW, n._b.w); maxD = Math.max(maxD, n.depth); });
    var cellW = maxW + 18, cellH = 84, pad = 16;
    (function place(n) {
      if (!n.children.length) { n._x = slot++; return; }
      n.children.forEach(place);
      n._x = (n.children[0]._x + n.children[n.children.length - 1]._x) / 2;
    })(list[0]);
    var W = Math.max(1, slot) * cellW + pad * 2, H = maxD * cellH + 58 + pad * 2, out = svgOpen(W, H), auto = [];
    list.forEach(function (n) { n._cx = pad + n._x * cellW + cellW / 2; n._cy = pad + 29 + n.depth * cellH; });
    list.forEach(function (n) {
      if (!n.parent) return;
      var p = n.parent, p1 = clipToBox(p._cx, p._cy, p._b.w / 2, p._b.h / 2, n._cx, n._cy, s.shape), p2 = clipToBox(n._cx, n._cy, n._b.w / 2, n._b.h / 2, p._cx, p._cy, s.shape);
      out += group(p.id + '>' + n.id, '<line class="d-line ls-draw" stroke-width="1.6" x1="' + r1(p1[0]) + '" y1="' + r1(p1[1]) + '" x2="' + r1(p2[0]) + '" y2="' + r1(p2[1]) + '"/>');
    });
    list.forEach(function (n) {
      out += group(n.id, drawNode({ label: n.label, sub: n.sub, style: n.style, shape: s.shape }, n._cx, n._cy, n._b));
      (auto[n.depth] = auto[n.depth] || []).push(n.id);
      if (n.parent) auto[n.depth].push(n.parent.id + '>' + n.id);
    });
    return { svg: out + '</svg>', auto: auto };
  };

  /* ---------------- bars ---------------- */
  V.bars = function (s) {
    var vals = s.values || [], labels = s.labels || [], n = vals.length, W = 640, H = 340, L = 50, R = 20, T = 28, B = 48;
    var top = s.max != null ? s.max : Math.max.apply(null, vals.concat([0])) || 1, ticks = niceTicks(0, top, 4);
    if (s.max == null) top = Math.max(top, ticks[ticks.length - 1] || top);
    var sy = function (v) { return H - B - Math.max(0, v) / top * (H - T - B); };
    var slot = (W - L - R) / Math.max(1, n), bw = Math.min(72, slot * 0.62), hi = {};
    (s.highlight || []).forEach(function (k) { hi[k] = 1; });
    var ax = '<line class="d-line" stroke-width="1.5" x1="' + L + '" y1="' + (H - B) + '" x2="' + (W - R) + '" y2="' + (H - B) + '"/>';
    ticks.forEach(function (v) {
      ax += '<line class="d-muted" stroke-width="1" opacity=".35" x1="' + L + '" y1="' + r1(sy(v)) + '" x2="' + (W - R) + '" y2="' + r1(sy(v)) + '"/>' + text(L - 8, sy(v) + 4, fmt(v), 'd-text-muted', 'end');
    });
    if (s.ylabel) ax += text(L - 40, T - 10, s.ylabel, 'd-text-muted', 'start');
    var out = svgOpen(W, H) + group('axes', ax), auto = [['axes']];
    vals.forEach(function (v, k) {
      var cx = L + slot * (k + 0.5), y = sy(v), id = 'b' + (k + 1);
      var body = '<rect class="' + (hi[k + 1] || !s.highlight ? 'd-fill-accent' : 'd-fill') + '" stroke-width="1.5" x="' + r1(cx - bw / 2) + '" y="' + r1(y) + '" width="' + r1(bw) + '" height="' + r1(H - B - y) + '" rx="3"/>' +
        text(cx, y - 7, fmt(v) + (s.unit || ''), hi[k + 1] ? 'd-text-accent' : 'd-text') + text(cx, H - B + 19, labels[k] == null ? '' : labels[k], 'd-text-muted');
      out += group(id, body); auto.push([id]);
    });
    return { svg: out + '</svg>', auto: auto };
  };

  /* ---------------- layers: fully connected columns of units ---------------- */
  V.layers = function (s) {
    var layers = (s.layers || []).map(function (l) { return typeof l === 'number' ? { n: l } : l; });
    var cap = s.max || 6, rad = 15, gapY = 44, colW = Math.max(120, 620 / Math.max(1, layers.length)), pad = 20;
    var maxShown = 0;
    layers.forEach(function (l) { l._k = Math.min(l.n, cap); l._cut = l.n > cap; maxShown = Math.max(maxShown, l._k); });
    var H = maxShown * gapY + pad * 2 + 34, W = layers.length * colW, out = svgOpen(W, H), auto = [];
    layers.forEach(function (l, i) {
      l._x = colW * (i + 0.5); l._ys = [];
      var y0 = pad + (maxShown * gapY - l._k * gapY) / 2 + gapY / 2;
      for (var k = 0; k < l._k; k++) l._ys.push(y0 + k * gapY);
    });
    for (var i = 0; i + 1 < layers.length; i++) {
      var a = layers[i], b = layers[i + 1], body = '';
      a._ys.forEach(function (ya, ka) { if (a._cut && ka === a._k - 2) return; b._ys.forEach(function (yb, kb) { if (b._cut && kb === b._k - 2) return;
        body += '<line class="d-muted" stroke-width="1" opacity=".7" x1="' + r1(a._x + rad) + '" y1="' + r1(ya) + '" x2="' + r1(b._x - rad) + '" y2="' + r1(yb) + '"/>'; }); });
      out += group('E' + (i + 1), body);
    }
    layers.forEach(function (l, i) {
      var body = '', cls = l.style === 'accent' ? 'd-fill-accent' : 'd-fill';
      l._ys.forEach(function (y, k) {
        if (l._cut && k === l._k - 2) { body += text(l._x, y + 6, '⋮', 'd-text'); return; }
        body += '<circle class="' + cls + '" stroke-width="1.5" cx="' + r1(l._x) + '" cy="' + r1(y) + '" r="' + rad + '"/>';
        var idx = l._cut && k === l._k - 1 ? l.n - 1 : k;
        if (l.nodes && l.nodes[idx] != null) body += text(l._x, y + 4, l.nodes[idx], 'd-text-muted');
      });
      if (l.label) body += text(l._x, H - 22, l.label, 'd-text');
      if (l.sub || l._cut) body += text(l._x, H - 6, l.sub || (l.n + ' units'), 'd-text-muted');
      out += group('L' + (i + 1), body);
      auto.push(i ? ['E' + i, 'L' + (i + 1)] : ['L1']);
    });
    return { svg: out + '</svg>', auto: auto };
  };

  /* ---------------- grid: matrices, arrays, tables of cells, with highlightable cells ---------------- */
  V.gridList = function (s) { return s.grids || [{ id: '', cells: s.cells || [], label: s.label, style: s.style, op: s.op }]; };
  V.grid = function (s) {
    var grids = V.gridList(s), size = s.cell || 40, pad = 16, x = pad, maxRows = 0, hasLabel = false;
    grids.forEach(function (g) { maxRows = Math.max(maxRows, (g.cells || []).length); if (g.label) hasLabel = true; });
    var top = pad + (hasLabel ? 24 : 0), H = top + maxRows * size + pad, out = '', auto = [];
    grids.forEach(function (g) {
      var rows = g.cells || [], cols = 0, wide = size;
      rows.forEach(function (r) { cols = Math.max(cols, r.length); r.forEach(function (v) { wide = Math.max(wide, textW(v == null ? '' : v) + 14); }); });
      if (g.op) { out += text(x + 14, top + maxRows * size / 2 + 7, g.op, 'd-text', 'middle', ' font-size="22"'); x += 34; }
      var y0 = top + (maxRows - rows.length) * size / 2, pre = g.id ? g.id + '.' : '', body = '';
      if (g.label) body += text(x + cols * wide / 2, y0 - 9, g.label, 'd-text-muted');
      rows.forEach(function (r, i) {
        r.forEach(function (v, j) {
          if (v === null) return;
          body += group(pre + 'r' + (i + 1) + 'c' + (j + 1),
            '<rect class="' + (g.style === 'accent' ? 'd-fill-accent' : 'd-fill') + '" stroke-width="1.2" x="' + r1(x + j * wide) + '" y="' + r1(y0 + i * size) + '" width="' + r1(wide) + '" height="' + size + '"/>' +
            text(x + j * wide + wide / 2, y0 + i * size + size / 2 + 5, v, 'd-text'));
        });
      });
      out += group(g.id || 'grid', body);
      x += cols * wide + 18;
    });
    return { svg: svgOpen(x - 18 + pad, H) + out + '</svg>', auto: auto };
  };
  /* "in.row2", "col1", "k.r1c1:r3c3", "in" -> element ids. Unknown tokens pass through unchanged. */
  V.gridExpand = function (s, token) {
    var grids = V.gridList(s), dot = token.lastIndexOf('.'), gid = dot < 0 ? '' : token.slice(0, dot), rest = dot < 0 ? token : token.slice(dot + 1);
    var g = null;
    grids.forEach(function (x) { if ((x.id || '') === gid) g = x; });
    if (!g) return [token];
    var rows = g.cells || [], pre = gid ? gid + '.' : '', out = [], m;
    function add(i, j) { if (rows[i - 1] && rows[i - 1][j - 1] != null) out.push(pre + 'r' + i + 'c' + j); }
    if ((m = rest.match(/^row(\d+)$/))) { for (var j = 1; j <= (rows[+m[1] - 1] || []).length; j++) add(+m[1], j); return out; }
    if ((m = rest.match(/^col(\d+)$/))) { for (var i = 1; i <= rows.length; i++) add(i, +m[1]); return out; }
    if ((m = rest.match(/^r(\d+)c(\d+):r(\d+)c(\d+)$/))) { for (var a = +m[1]; a <= +m[3]; a++) for (var b = +m[2]; b <= +m[4]; b++) add(a, b); return out; }
    return [token];
  };

  V.kinds = ['plot', 'flow', 'tree', 'bars', 'layers', 'grid'];
})();
