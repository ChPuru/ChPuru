"""Draw text as glyph outlines so the README SVGs look identical everywhere.

GitHub serves SVG files from a repo with

    Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; sandbox

so CSS animations work, but @font-face is blocked (even as a data: URI) and
<text> falls back to whatever fonts the viewer has. Instead, every character
here is a Maple Mono outline from glyphs.json, defined once in <defs> and
placed with <use>. Standard library only.
"""
from __future__ import annotations

import json
from pathlib import Path

GLYPHS = Path(__file__).with_name("glyphs.json")


class Typesetter:
    def __init__(self, path: Path = GLYPHS) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.upm: int = data["upm"]
        self.advance: int = data["advance"]
        self.weights: dict[str, dict[str, str]] = data["weights"]
        self.bounds: dict[str, dict[str, list[int]]] = data.get("bounds", {})
        self.wide: dict[str, int] = data.get("wide", {})
        self._used: dict[str, str] = {}

    def has(self, ch: str, weight: str | int = "400") -> bool:
        return ch in self.weights[str(weight)]

    def char_width(self, ch: str, size: float) -> float:
        return self.wide.get(ch, self.advance) * size / self.upm

    def width(self, text: str, size: float) -> float:
        return sum(self.char_width(ch, size) for ch in text)

    def extent(self, text: str, size: float, weight: str | int = "400") -> tuple[float, float]:
        """Top and bottom of the inked area as offsets from the baseline (SVG y grows down)."""
        table = self.bounds.get(str(weight), {})
        boxes = [table[ch] for ch in text if ch in table]
        if not boxes:
            return (-0.73 * size, 0.0)
        s = size / self.upm
        return (-max(b[3] for b in boxes) * s, -min(b[1] for b in boxes) * s)

    def text(self, text: str, x: float, y: float, size: float,
             weight: str | int = "400", **attrs: object) -> str:
        """One <g> of <use> elements, baseline at (x, y). Keyword args become
        attributes: class_="a" -> class="a", stroke_width=2 -> stroke-width="2"."""
        weight = str(weight)
        table = self.weights[weight]
        s = size / self.upm
        uses: list[str] = []
        cx = x
        for ch in text:
            if ch not in table:
                ch = "?"
            d = table[ch]
            if d:
                gid = f"g{weight}-{ord(ch):x}"
                self._used[gid] = d
                uses.append(f'<use href="#{gid}" transform="translate({cx:.2f} {y:.2f}) '
                            f'scale({s:.5f} {-s:.5f})"/>')
            cx += self.char_width(ch, size)
        attr = "".join(f' {k.rstrip("_").replace("_", "-")}="{v}"'
                       for k, v in attrs.items() if v is not None)
        return f"<g{attr}>{''.join(uses)}</g>"

    def defs(self) -> str:
        """Call after all text(): one <path> per glyph actually used."""
        return "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in sorted(self._used.items()))
