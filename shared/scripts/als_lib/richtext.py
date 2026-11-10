"""Rich-text (Markdown-lite + $maths$) conversion for non-browser outputs (Anki, TSV)."""
from __future__ import annotations

import html
import re

MATH = re.compile(r"\$\$([\s\S]+?)\$\$|\$(?!\s)((?:\\\$|[^$\n])+?)(?<!\s)\$(?!\d)")
CODE = re.compile(r"`([^`\n]+)`")


def _inline(s: str) -> str:
    s = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(^|[^*\w])\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\w)", r"\1<i>\2</i>", s)
    return s


def to_html(text: str | None, anki_math: bool = True) -> str:
    """Convert rich text to simple HTML. Maths becomes Anki MathJax delimiters \\( \\) and \\[ \\]."""
    if not text:
        return ""
    held: list[str] = []

    def hold(v: str) -> str:
        held.append(v)
        return f"\x00{len(held) - 1}\x00"

    s = str(text).replace("\r\n", "\n")
    s = CODE.sub(lambda m: hold("<code>" + html.escape(m.group(1)) + "</code>"), s)

    def math(m: re.Match) -> str:
        if m.group(1) is not None:
            tex = html.escape(m.group(1).strip(), quote=False)
            return hold(r"\[" + tex + r"\]" if anki_math else "$$" + tex + "$$")
        tex = html.escape(m.group(2).strip(), quote=False)
        return hold(r"\(" + tex + r"\)" if anki_math else "$" + tex + "$")

    s = MATH.sub(math, s)
    s = html.escape(s, quote=False)
    blocks = []
    for block in re.split(r"\n{2,}", s):
        lines = block.split("\n")
        if all(re.match(r"^\s*[-*•]\s+", ln) for ln in lines if ln.strip()) and block.strip():
            blocks.append("<ul>" + "".join("<li>" + _inline(re.sub(r"^\s*[-*•]\s+", "", ln)) + "</li>" for ln in lines if ln.strip()) + "</ul>")
        elif all(re.match(r"^\s*\d+[.)]\s+", ln) for ln in lines if ln.strip()) and block.strip():
            blocks.append("<ol>" + "".join("<li>" + _inline(re.sub(r"^\s*\d+[.)]\s+", "", ln)) + "</li>" for ln in lines if ln.strip()) + "</ol>")
        else:
            blocks.append(_inline(block).replace("\n", "<br>"))
    out = "<br><br>".join(b for b in blocks if b)
    return re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], out)


def to_plain(text: str | None) -> str:
    """Strip formatting for plain-text exports (Quizlet). Maths keeps its TeX source."""
    if not text:
        return ""
    s = str(text)
    s = re.sub(r"\*\*([^*]+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\w)\*([^*\n]+?)\*(?!\w)", r"\1", s)
    s = CODE.sub(r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r"\1 (\2)", s)
    return " ".join(s.split())
