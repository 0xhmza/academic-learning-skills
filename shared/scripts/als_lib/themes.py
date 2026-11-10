"""Pick a design system for a subject."""
from __future__ import annotations

import re
from functools import lru_cache

from .paths import DESIGN, read_json


@lru_cache(maxsize=1)
def registry() -> dict:
    return read_json(DESIGN / "themes.json")


def names() -> list[str]:
    return list(registry()["themes"])


def route(*texts: str | None) -> tuple[str, str]:
    """Return (theme, reason). Longest keyword match wins, matched on word boundaries."""
    reg = registry()
    hay = " ".join(t for t in texts if t).lower()
    best: tuple[int, str, str] | None = None
    if hay:
        for name, theme in reg["themes"].items():
            for kw in theme.get("subjects", []):
                if re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", hay):
                    if best is None or len(kw) > best[0]:
                        best = (len(kw), name, kw)
    if best:
        return best[1], f"matched subject keyword '{best[2]}'"
    return reg["default"], "no subject keyword matched; using the default"


def css_bundle() -> str:
    parts = [(DESIGN / "base.css").read_text(encoding="utf-8")]
    for name in names():
        parts.append((DESIGN / f"{name}.css").read_text(encoding="utf-8"))
    return "\n".join(parts)


def runtime_registry() -> dict:
    """The subset of themes.json the page needs (no subject keyword lists)."""
    return {
        name: {k: v for k, v in t.items() if k != "subjects"}
        for name, t in registry()["themes"].items()
    }
