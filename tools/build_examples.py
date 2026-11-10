"""Build every example data file into examples/showcase/ (HTML, plus .apkg for decks).

    python tools/build_examples.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "shared" / "scripts"))

from als_lib import anki, build, paths  # noqa: E402


def main() -> int:
    out_dir = ROOT / "examples" / "showcase"
    out_dir.mkdir(parents=True, exist_ok=True)
    rc = 0
    for src in sorted((ROOT / "examples").glob("*/*.json")):
        if src.parent.name == "showcase":
            continue
        name = f"{src.parent.name}-{src.stem}"
        try:
            out, theme, why, warns = build.build_file(src, out_dir / f"{name}.html", ws=None, embed_due=False)
        except build.BuildError as exc:
            print(f"FAIL {src}: {exc}")
            rc = 1
            continue
        print(f"{out.relative_to(ROOT)}  [{theme}: {why}]")
        for w in warns:
            print(f"  warning {w}")
        data = paths.read_json(src)
        if data["kind"] == "deck" and anki.has_genanki():
            p, n = anki.to_apkg(data, out_dir / f"{name}.apkg")
            print(f"{p.relative_to(ROOT)}  [{n} notes]")
    return rc


if __name__ == "__main__":
    sys.exit(main())
