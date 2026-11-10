"""SessionStart hook: print a compact study status if a learner workspace exists.

Prints nothing (and costs no context) when there is no workspace in $ALS_HOME or ./study.
Never fails the session: all errors are swallowed.
"""
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared" / "scripts"))
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    from als_lib import paths, report

    ws = paths.workspace()
    if (ws / "profile.md").exists():
        text = report.status_text(ws, max_lines=8)
        if text:
            print("[academic-learning-skills] " + text.replace("\n", "\n  "))
            print("  Apply the Remember/Avoid preferences above to study material in this session.")
except Exception:  # a broken workspace must never block the session
    pass
