/* Tests for the string functions of core.js. Run: node tests/js/test_core.js */
const assert = require('assert');
const { load, show } = require('./harness');

const ALS = load(['i18n.js', 'core.js']).ALS;
const md = (s) => show(ALS.md(s, { inline: true }));

// [input, expected]; ⟦…⟧ marks text that is typeset as maths
const CASES = [
  // explicit delimiters
  ['It crosses 0.5 at $z = 0$.', 'It crosses ⟦0.5⟧ at ⟦z = 0⟧.'],
  ['$ x = 3 $ padded', '⟦x = 3⟧ padded'],
  ['Price: $5 and $10 today', 'Price: $5 and $10 today'],
  ['\\begin{aligned} a &= b \\\\ c &= d \\end{aligned}', '⟦⟦\\begin{aligned} a &= b \\\\ c &= d \\end{aligned}⟧⟧'],
  // Unicode maths without delimiters
  ['The curve σ(z) rises from 0 to 1.', 'The curve ⟦\\sigma (z)⟧ rises from ⟦0⟧ to ⟦1⟧.'],
  ['We get x₁ + x₂ ≤ 5 here', 'We get ⟦x_{1} + x_{2} \\le  5⟧ here'],
  ['Cost is O(n²) in the worst case', 'Cost is ⟦O(n^{2})⟧ in the worst case'],
  ['(x₁, x₂) ∈ ℝ²', '⟦(x_{1}, x_{2}) \\in  \\mathbb{R}^{2}⟧'],
  ['∂L/∂w is the gradient', '⟦\\partial L/\\partial w⟧ is the gradient'],
  ['wᵀx + b > 0', '⟦w^{T}x + b > 0⟧'],
  ['ŷ = 0.9 predicted', '⟦\\hat{y} = 0.9⟧ predicted'],
  ['sin(x) ≈ x for small x', '⟦\\operatorname{sin}(x) \\approx  x⟧ for small x'],
  ['H₂O and CO₂ are molecules', '⟦\\mathrm{H_{2}O}⟧ and ⟦\\mathrm{CO_{2}}⟧ are molecules'],
  // plain-text equations and powers
  ['so f(3) = 6 and x = 3', 'so ⟦f(3) = 6⟧ and ⟦x = 3⟧'],
  ['f(x) = x^2, so f(3) = 9', '⟦f(x) = x^2⟧, so ⟦f(3) = 9⟧'],
  ['E = mc^2 and e^{-x}', '⟦E = mc^2⟧ and ⟦e^{-x}⟧'],
  ['p < 0.05 means significant', '⟦p < 0.05⟧ means significant'],
  ['T(n) = 2T(n/2) + n', '⟦T(n) = 2T(n/2) + n⟧'],
  ['**x = 3** is bold', '<strong>⟦x = 3⟧</strong> is bold'],
  ['Der Wert n = 10 und 3,5 Punkte', 'Der Wert ⟦n = 10⟧ und ⟦3{,}5⟧ Punkte'],
  ['a 50% chance with $p$', 'a ⟦50\\%⟧ chance with ⟦p⟧'],
  ["تساوي المشتقة f'(x) = 2x عند 3", "تساوي المشتقة ⟦f'(x) = 2x⟧ عند ⟦3⟧"],
  // ordinary text must stay untouched
  ['Lecture 3 covers this in 1905.', 'Lecture 3 covers this in 1905.'],
  ['no maths here, 3 apples and 4.5 pears', 'no maths here, 3 apples and 4.5 pears'],
  ['Use my_var and snake_case here', 'Use my_var and snake_case here'],
  ['I = me, said the author', 'I = me, said the author'],
  ['The λόγος of Heraclitus', 'The λόγος of Heraclitus'],
  ['Section 2.1 (see L3 s.12)', 'Section 2.1 (see L3 s.12)'],
  ['Größe und Maß', 'Größe und Maß'],
  ['1. First item\n2. Second with $a$ and 7', '1. First item<br>2. Second with ⟦a⟧ and ⟦7⟧'],
  ['Use `x = 3` in code', 'Use <code>x = 3</code> in code'],
];

let failed = 0;
for (const [input, want] of CASES) {
  const got = md(input);
  if (got !== want) { failed++; console.log('FAIL', JSON.stringify(input), '\n   got ', got, '\n   want', want); }
}

assert.strictEqual(ALS.tex('$$x^2$$'), 'x^2');
assert.strictEqual(ALS.tex('$a$'), 'a');
assert.strictEqual(ALS.tex('\\[ q \\]'), 'q');
assert.strictEqual(ALS.tex('a+b'), 'a+b');

// automatic maths can be switched off per file
ALS.autoMathOn = false;
assert.strictEqual(md('x = 3 and σ'), 'x = 3 and σ');
ALS.autoMathOn = true;

// raw HTML is always escaped
assert.ok(ALS.md('<img src=x onerror=alert(1)>').indexOf('<img') < 0);

// i18n: every language answers, placeholders are filled, unknown keys fall back to English
ALS.lang = 'ar';
assert.notStrictEqual(ALS.t('Show answer'), 'Show answer');
assert.ok(ALS.t('Card {0} of {1}', 2, 9).indexOf('2') > -1);
assert.strictEqual(ALS.t('no such key {0}', 'x'), 'no such key x');
ALS.lang = 'en';
assert.strictEqual(ALS.t('Card {0} of {1}', 2, 9), 'Card 2 of 9');

if (failed) { console.log(failed + ' of ' + CASES.length + ' maths cases failed'); process.exit(1); }
console.log('ok: ' + CASES.length + ' maths cases, tex(), escaping, i18n');
