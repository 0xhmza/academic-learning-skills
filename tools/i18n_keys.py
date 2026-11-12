"""List the interface strings used by the templates and check that every language translates them.

    python tools/i18n_keys.py            # report missing and unused keys per language
    python tools/i18n_keys.py --list     # print every key

English strings are the keys: templates call T('Show answer'), shared/templates/i18n.js maps them.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "shared" / "templates"
CALL = re.compile(r"""\bT\(\s*(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")""")
ENTRY = re.compile(r"""^\s*(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")\s*:""", re.M)
# keys reached through a variable (T(x)) rather than a literal
INDIRECT = ["brief", "medium", "deep", "study", "present", "practice", "test", "Hidden", "Inline", "At the end",
            "Header", "Sidebar", "Controls", "Status bar",
            "Maths, physics, CS, engineering", "Philosophy, literature, history, arts",
            "Biology, medicine, chemistry, health", "Economics, business, law, social science"]


def unescape(s: str) -> str:
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def used_keys() -> list[str]:
    keys: list[str] = []
    for f in sorted(TEMPLATES.iterdir()):
        if f.name == "i18n.js" or f.suffix not in (".js", ".html"):
            continue
        for m in CALL.finditer(f.read_text(encoding="utf-8")):
            k = unescape(m.group(1) if m.group(1) is not None else m.group(2))
            if k and k not in keys:
                keys.append(k)
    for k in INDIRECT:
        if k not in keys:
            keys.append(k)
    return keys


def translations() -> dict[str, set[str]]:
    text = (TEMPLATES / "i18n.js").read_text(encoding="utf-8")
    out: dict[str, set[str]] = {}
    for m in re.finditer(r"^  (\w+): \{(.*?)^  \}", text, re.S | re.M):
        out[m.group(1)] = {unescape(a or b) for a, b in ENTRY.findall(m.group(2))}
    return out


def main() -> int:
    keys = used_keys()
    if "--list" in sys.argv:
        print("\n".join(keys))
        return 0
    bad = 0
    for lang, have in translations().items():
        missing = [k for k in keys if k not in have]
        unused = sorted(have - set(keys))
        print(f"{lang}: {len(have)} translated, {len(missing)} missing, {len(unused)} unused")
        for k in missing[:25]:
            print(f"  missing: {k}")
        for k in unused[:25]:
            print(f"  unused:  {k}")
        bad += len(missing)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
