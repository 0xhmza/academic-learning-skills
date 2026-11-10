"""Turn lecture PDFs into page-numbered text (and page images) so lessons can cite exact pages.

Uses whatever is installed: `pdftotext`/`pdftoppm` (Poppler, also shipped with Git for Windows,
TeX Live and MiKTeX), else the optional Python packages `pypdf` or `pymupdf`.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

THIN_CHARS = 40  # fewer visible characters than this: the page is probably a figure

_EXTRA_DIRS = [
    r"C:\Program Files\Git\mingw64\bin", r"C:\Program Files\Git\usr\bin", r"C:\msys64\ucrt64\bin", r"C:\msys64\mingw64\bin",
    "/opt/homebrew/bin", "/usr/local/bin",
]


def find_tool(name: str) -> str | None:
    hit = shutil.which(name)
    if hit:
        return hit
    for d in _EXTRA_DIRS:
        for cand in (Path(d) / name, Path(d) / (name + ".exe")):
            if cand.is_file():
                return str(cand)
    return None


def parse_pages(spec: str | None, total: int) -> list[int]:
    """'1-5,8,12-' -> page numbers (1-based), clipped to the document."""
    if not spec:
        return list(range(1, total + 1))
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(\d*)\s*-\s*(\d*)$", part)
        if m:
            a = int(m.group(1) or 1)
            b = int(m.group(2) or total)
        elif part.isdigit():
            a = b = int(part)
        else:
            raise ValueError(f"cannot read page range {part!r}; use e.g. 1-10,14")
        out.extend(range(max(1, a), min(total, b) + 1))
    return sorted(set(out))


def page_texts(pdf: Path, layout: bool = False) -> tuple[list[str], str]:
    """Text of every page, plus the name of the engine that produced it."""
    tool = find_tool("pdftotext")
    if tool:
        cmd = [tool, "-enc", "UTF-8"] + (["-layout"] if layout else []) + [str(pdf), "-"]
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode == 0:
            pages = res.stdout.decode("utf-8", "replace").split("\f")
            if pages and not pages[-1].strip():
                pages.pop()
            return pages, "pdftotext"
    try:
        import pypdf  # type: ignore
        reader = pypdf.PdfReader(str(pdf))
        return [(p.extract_text() or "") for p in reader.pages], "pypdf"
    except ImportError:
        pass
    try:
        import fitz  # type: ignore
        with fitz.open(str(pdf)) as doc:
            return [page.get_text() for page in doc], "pymupdf"
    except ImportError:
        pass
    raise RuntimeError("no PDF text extractor found: install Poppler (pdftotext) or run `pip install pypdf`")


def clean(text: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.replace("\r", "").split("\n")]
    out: list[str] = []
    for ln in lines:
        if ln or (out and out[-1]):
            out.append(ln)
    return "\n".join(out).strip()


_FOOTER = re.compile(r"^\s*(\d+\s*(/|of|von)\s*\d+|\d+)\s*$", re.I)


def _core(text: str) -> str:
    """Page text without page-number lines, whitespace collapsed: used to spot build-up slides."""
    return " ".join(ln.strip() for ln in text.split("\n") if ln.strip() and not _FOOTER.match(ln))


def build_ups(pages: list[str]) -> dict[int, int]:
    """Map page -> the later page that contains it, for slides that only add to the previous one."""
    cores = [_core(p) for p in pages]
    out: dict[int, int] = {}
    for i in range(len(pages) - 2, -1, -1):
        a, b = cores[i], cores[i + 1]
        if a and len(b) >= len(a) and b.startswith(a):
            out[i + 1] = out.get(i + 2, i + 2)
    return out


def render_pages(pdf: Path, pages: list[int], out_dir: Path, dpi: int = 80) -> dict[int, Path]:
    out: dict[int, Path] = {}
    if not pages:
        return out
    out_dir.mkdir(parents=True, exist_ok=True)
    tool = find_tool("pdftoppm")
    if tool:
        for n in pages:
            base = out_dir / f"{pdf.stem}-p{n:03d}"
            res = subprocess.run([tool, "-png", "-r", str(dpi), "-f", str(n), "-l", str(n), "-singlefile", str(pdf), str(base)], capture_output=True)
            if res.returncode == 0 and base.with_suffix(".png").exists():
                out[n] = base.with_suffix(".png")
        if out:
            return out
    try:
        import fitz  # type: ignore
    except ImportError:
        raise RuntimeError("no PDF renderer found: install Poppler (pdftoppm) or run `pip install pymupdf`") from None
    with fitz.open(str(pdf)) as doc:
        for n in pages:
            target = out_dir / f"{pdf.stem}-p{n:03d}.png"
            doc[n - 1].get_pixmap(dpi=dpi).save(str(target))
            out[n] = target
    return out


def extract(pdf: Path, out_dir: Path, pages: str | None = None, images: str = "none", dpi: int = 80,
            keep_builds: bool = False, layout: bool = False) -> dict:
    """Write <out_dir>/<stem>.txt with `=== <stem> p.N ===` headers and return a report."""
    pdf = Path(pdf)
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    raw, engine = page_texts(pdf, layout)
    texts = [clean(t) for t in raw]
    wanted = parse_pages(pages, len(texts))
    merged = {} if keep_builds else build_ups(texts)
    thin = [n for n in wanted if len(re.sub(r"\s", "", texts[n - 1])) < THIN_CHARS]
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{pdf.stem}.txt"
    parts: list[str] = []
    toc: list[tuple[int, str, int]] = []
    for n in wanted:
        if n in merged and merged[n] in wanted:
            continue
        body = texts[n - 1]
        head = [ln for ln in body.split("\n") if ln.strip()][:2]
        toc.append((n, " · ".join(head)[:90], len(body)))
        note = " (no text: figure or image, look at the page image)" if n in thin else ""
        parts.append(f"=== {pdf.stem} p.{n}{note} ===\n{body}\n")
    target.write_text("\n".join(parts), encoding="utf-8")
    shots: dict[int, Path] = {}
    if images != "none":
        shots = render_pages(pdf, wanted if images == "all" else thin, out_dir, dpi)
    return {
        "pdf": str(pdf), "text": target, "engine": engine, "pages": len(texts), "written": len(toc),
        "chars": sum(c for _, _, c in toc), "thin": thin, "merged": {k: v for k, v in merged.items() if k in wanted},
        "images": shots, "toc": toc,
    }


def ranges(nums: list[int]) -> str:
    """[1,2,3,7] -> '1-3, 7'"""
    out: list[str] = []
    start = prev = None
    for n in sorted(nums):
        if prev is not None and n == prev + 1:
            prev = n
            continue
        if start is not None:
            out.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = n
    if start is not None:
        out.append(str(start) if start == prev else f"{start}-{prev}")
    return ", ".join(out)
