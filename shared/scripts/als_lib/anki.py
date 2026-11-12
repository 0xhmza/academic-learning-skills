"""Export decks to Anki (.apkg via genanki, or importable TSV) and to Quizlet/CSV."""
from __future__ import annotations

import csv
import hashlib
import io
import re
from pathlib import Path

from .richtext import to_html, to_plain

CARD_CSS = """
.card { font-family: "Inter", "Segoe UI", system-ui, sans-serif; font-size: 20px; line-height: 1.5;
        color: #111827; background: #ffffff; text-align: center; padding: 18px; }
.nightMode.card, .night_mode .card { color: #f3f4f6; background: #0b1120; }
.extra { font-size: 15px; color: #4b5563; margin-top: 14px; border-top: 1px dashed #d1d5db; padding-top: 10px; text-align: left; }
.nightMode .extra { color: #9ca3af; border-color: #374151; }
.src { font-family: ui-monospace, Consolas, monospace; font-size: 11px; color: #9ca3af; margin-top: 12px; }
.cloze { font-weight: 600; color: #0284c7; }
.nightMode .cloze { color: #38bdf8; }
code { font-family: ui-monospace, Consolas, monospace; font-size: .9em; background: rgba(127,127,127,.12); padding: 0 .25em; border-radius: 4px; }
ul, ol { text-align: left; display: inline-block; }
"""


def _stable_id(*parts: str) -> int:
    h = hashlib.sha1("\x1f".join(parts).encode("utf-8")).hexdigest()
    return int(h[:12], 16) % (1 << 30) + (1 << 30)  # 31-bit positive, never collides with Anki's small defaults


def _tags(card: dict, module: str | None) -> list[str]:
    tags = []
    for t in card.get("tags", []) or []:
        t = re.sub(r"\s+", "_", t.strip())
        if t:
            tags.append(t)
    if card.get("topic"):
        tags.append("topic::" + re.sub(r"\s+", "_", card["topic"]))
    if module:
        tags.append("module::" + module)
    if card.get("grounded") is False:
        tags.append("beyond_notes")
    return tags


def _deck_name(deck: dict) -> str:
    title = deck["title"].replace("::", ":")
    return f"{deck['module']}::{title}" if deck.get("module") else title


RTL_LANGS = {"ar", "he", "fa", "ur", "ps", "sd", "ckb", "yi", "dv", "ug"}


def _rtl(deck: dict) -> bool:
    if deck.get("dir") in ("rtl", "ltr"):
        return deck["dir"] == "rtl"
    return str(deck.get("lang") or "en").split("-")[0].lower() in RTL_LANGS


def _field(deck: dict, text: str | None) -> str:
    """Rich text as card HTML; right-to-left decks get a dir wrapper so Anki aligns them correctly."""
    h = to_html(text)
    return f'<div dir="rtl">{h}</div>' if h and _rtl(deck) else h


def has_genanki() -> bool:
    try:
        import genanki  # noqa: F401
        return True
    except ImportError:
        return False


def to_apkg(deck: dict, out: Path) -> tuple[Path, int]:
    import genanki

    basic = genanki.Model(
        _stable_id("als-model-basic-v1"), "ALS Basic",
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Extra"}, {"name": "Source"}],
        templates=[{
            "name": "Card 1",
            "qfmt": "{{Front}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Back}}{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}{{#Source}}<div class="src">{{Source}}</div>{{/Source}}',
        }],
        css=CARD_CSS,
    )
    reverse = genanki.Model(
        _stable_id("als-model-reverse-v1"), "ALS Basic (and reversed)",
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Extra"}, {"name": "Source"}],
        templates=[
            {"name": "Card 1", "qfmt": "{{Front}}", "afmt": '{{FrontSide}}<hr id="answer">{{Back}}{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}{{#Source}}<div class="src">{{Source}}</div>{{/Source}}'},
            {"name": "Card 2", "qfmt": "{{Back}}", "afmt": '{{FrontSide}}<hr id="answer">{{Front}}{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}{{#Source}}<div class="src">{{Source}}</div>{{/Source}}'},
        ],
        css=CARD_CSS,
    )
    cloze = genanki.Model(
        _stable_id("als-model-cloze-v1"), "ALS Cloze",
        fields=[{"name": "Text"}, {"name": "Extra"}, {"name": "Source"}],
        templates=[{
            "name": "Cloze",
            "qfmt": "{{cloze:Text}}",
            "afmt": '{{cloze:Text}}{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}{{#Source}}<div class="src">{{Source}}</div>{{/Source}}',
        }],
        css=CARD_CSS,
        model_type=genanki.Model.CLOZE,
    )
    name = _deck_name(deck)
    gdeck = genanki.Deck(_stable_id("als-deck", deck.get("module") or "", deck["title"]), name)
    gdeck.description = deck.get("subtitle", "")
    for c in deck["cards"]:
        guid = genanki.guid_for("als", deck.get("module") or "", deck["title"], c["id"])
        src = c.get("src", "")
        if c["type"] == "cloze":
            note = genanki.Note(model=cloze, fields=[_field(deck, c["text"]), _field(deck, c.get("extra")), src], tags=_tags(c, deck.get("module")), guid=guid)
        else:
            model = reverse if c["type"] == "reverse" else basic
            note = genanki.Note(model=model, fields=[_field(deck, c["front"]), _field(deck, c["back"]), _field(deck, c.get("extra")), src], tags=_tags(c, deck.get("module")), guid=guid)
        gdeck.add_note(note)
    out.parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(gdeck).write_to_file(str(out))
    return out, len(deck["cards"])


def to_anki_tsv(deck: dict, out: Path) -> tuple[Path, int]:
    """Anki 2.1.55+ text import with file headers (File > Import)."""
    buf = io.StringIO()
    buf.write("#separator:tab\n#html:true\n#notetype column:1\n#deck column:2\n#tags column:6\n")
    w = csv.writer(buf, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    name = _deck_name(deck)
    for c in deck["cards"]:
        tags = " ".join(_tags(c, deck.get("module")))
        if c["type"] == "cloze":
            w.writerow(["Cloze", name, _field(deck, c["text"]), _field(deck, c.get("extra")), c.get("src", ""), tags])
        else:
            nt = "Basic (and reversed card)" if c["type"] == "reverse" else "Basic"
            w.writerow([nt, name, _field(deck, c["front"]), _field(deck, c["back"]), c.get("src", ""), tags])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(buf.getvalue(), encoding="utf-8")
    return out, len(deck["cards"])


def to_quizlet(deck: dict, out: Path) -> tuple[Path, int]:
    """Plain 'term<TAB>definition' lines for Quizlet import. Cloze cards become sentence/answer pairs."""
    rows = []
    for c in deck["cards"]:
        if c["type"] == "cloze":
            text = c["text"]
            answers = [m.group(1) for m in re.finditer(r"\{\{c\d+::([\s\S]*?)(?:::[\s\S]*?)?\}\}", text)]
            blanked = re.sub(r"\{\{c\d+::([\s\S]*?)(?:::[\s\S]*?)?\}\}", "____", text)
            rows.append((to_plain(blanked), to_plain("; ".join(answers))))
        else:
            rows.append((to_plain(c["front"]), to_plain(c["back"])))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(f"{a}\t{b}" for a, b in rows) + "\n", encoding="utf-8")
    return out, len(rows)


def to_csv(deck: dict, out: Path) -> tuple[Path, int]:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "type", "front", "back", "text", "extra", "tags", "topic", "src"])
        for c in deck["cards"]:
            w.writerow([c["id"], c["type"], c.get("front", ""), c.get("back", ""), c.get("text", ""), c.get("extra", ""), " ".join(c.get("tags", []) or []), c.get("topic", ""), c.get("src", "")])
    return out, len(deck["cards"])
