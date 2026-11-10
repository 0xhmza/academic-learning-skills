"""Print a built page to PDF with a headless Chromium-family browser, if one is installed."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

CANDIDATES = [
    "chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge", "microsoft-edge", "brave", "brave-browser",
]
WINDOWS = [
    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
    r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe",
]
MAC = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]


def find_browser() -> str | None:
    env = os.environ.get("ALS_BROWSER")
    if env and Path(env).exists():
        return env
    for name in CANDIDATES:
        p = shutil.which(name)
        if p:
            return p
    for raw in WINDOWS + MAC:
        p = Path(os.path.expandvars(raw))
        if "%" not in str(p) and p.exists():
            return str(p)
    return None


def print_pdf(html_file: Path, out: Path, query: str = "") -> Path:
    browser = find_browser()
    if not browser:
        raise RuntimeError(
            "no Chrome, Edge, Chromium or Brave found (set ALS_BROWSER to its path). "
            f"Open {html_file} in a browser and use Print > Save as PDF instead."
        )
    url = html_file.resolve().as_uri() + (("?" + query.lstrip("?")) if query else "")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
           "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000", f"--print-to-pdf={out.resolve()}", url]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not out.exists():
        raise RuntimeError(f"browser did not write the PDF (exit {res.returncode}): {res.stderr.strip()[:400]}")
    return out
