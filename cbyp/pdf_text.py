"""Text in a PDF that a person can't see, found in plain code.

Spark reads a PDF note from its rendered pages, and on 28 Oct it never saw lines written in
white 2 pt text, while the PDF's text layer (what other importers read) still carried them.
This looks at every character's fill colour and size instead of asking a model.
"""
from pathlib import Path

import pdfplumber

# Under 4 pt is unreadable on a printed A4 page. Only white or tiny counts as invisible: a
# scanned PDF's OCR layer is invisible too, but at normal size and not white, and must pass.
MIN_SIZE = 4.0
WHITE = 0.95


def _white(color) -> bool:
    """Fill colour as pdfplumber gives it: gray (1 value), RGB (3) or CMYK (4)."""
    if color is None:
        return False
    c = tuple(color) if isinstance(color, (tuple, list)) else (color,)
    if len(c) == 4:
        return all(v <= 1 - WHITE for v in c)
    return all(isinstance(v, (int, float)) and v >= WHITE for v in c)


def invisible_lines(path) -> list[str]:
    """Lines of white or tiny text in a PDF, in reading order; [] for anything else."""
    path = Path(path)
    if path.suffix.lower() != ".pdf":
        return []
    lines = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            rows: dict[float, list] = {}
            for ch in page.chars:
                if ch["size"] < MIN_SIZE or _white(ch.get("non_stroking_color")):
                    rows.setdefault(round(ch["top"], 1), []).append(ch)
            for top in sorted(rows):
                text = "".join(c["text"] for c in sorted(rows[top], key=lambda c: c["x0"]))
                if text.strip():
                    lines.append(" ".join(text.split()))
    return lines
