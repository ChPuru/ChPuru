#!/usr/bin/env python3
"""Build assets/bsod.svg, the header of the GitHub profile.

A blue screen counts up to 100%, the sad face glitches, and a smile takes
its place. Plain SVG + CSS, because GitHub runs no scripts inside README
images. With prefers-reduced-motion the file shows its last frame.

Edit the copy below, then rebuild:
    pip install segno
    python3 scripts/build_hero.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from string import Template

import segno

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgtype import Typesetter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "bsod.svg"
QR_URL = "https://www.linkedin.com/in/purunjay-choudhary"

# ---- copy ------------------------------------------------------------------
NAME = "Purunjay Choudhary"
LINES = [
    "Computer engineering student at KJSCE, Mumbai.",
    "I build operating systems, compilers and databases.",
]
FINE = "Scan to connect on LinkedIn."
STOP = "Stop code: BUILT_FROM_SCRATCH"

# ---- timeline (seconds) ----------------------------------------------------
# (percent, starts at, visible for); "100% complete" stays from DONE on
FRAMES = [(0, 0.00, 0.40), (14, 0.40, 0.45), (29, 0.85, 0.40), (43, 1.25, 0.45),
          (57, 1.70, 0.35), (71, 2.05, 0.45), (86, 2.50, 0.40), (95, 2.90, 0.35)]
DONE = 3.25
GLITCH = 3.30  # the sad face starts breaking
FIXED = 3.65   # the smile replaces it

# ---- look ------------------------------------------------------------------
W, H, M = 840, 472, 56
BLUE_HI, BLUE_LO = "#4b5df2", "#2231b0"
INK, INK_SOFT = "#f4f6ff", "#d3d9ff"
MINT, PINK, CYAN, QR_DARK = "#b8f5d8", "#ffb3d1", "#8ef3ff", "#1b248c"

CSS = Template("""
.fr{opacity:0}
.sad{opacity:0;animation:on ${fixed}s linear}
.ga,.gb,.tear,.flash{opacity:0}
.jit{animation:jit ${glen}s steps(1,end) ${glitch}s}
.ga{animation:ga ${glen}s steps(1,end) ${glitch}s}
.gb{animation:gb ${glen}s steps(1,end) ${glitch}s}
.tear{animation:tear ${glen}s steps(1,end) ${glitch}s}
.done{animation:off .01s linear ${done}s backwards}
.fix{transform-box:fill-box;transform-origin:50% 55%;animation:pop .5s cubic-bezier(.2,1.5,.45,1) ${fixed}s backwards}
.flash{animation:flash .4s ease-out ${fixed}s}
@keyframes on{from,to{opacity:1}}
@keyframes off{from,to{opacity:0}}
@keyframes pop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:scale(1)}}
@keyframes flash{from{opacity:.22}to{opacity:0}}
@keyframes jit{0%{transform:translate(0,0)}15%{transform:translate(-7px,1px)}30%{transform:translate(5px,-2px)}45%{transform:translate(-3px,0)}60%{transform:translate(9px,1px)}75%{transform:translate(-5px,-1px)}90%{transform:translate(2px,0)}}
@keyframes ga{0%{opacity:.85;transform:translate(-6px,0)}20%{opacity:0}35%{opacity:.9;transform:translate(-11px,2px)}55%{opacity:.3;transform:translate(4px,-1px)}70%{opacity:.85;transform:translate(-7px,1px)}90%,100%{opacity:0}}
@keyframes gb{0%{opacity:.7;transform:translate(6px,0)}20%{opacity:.9;transform:translate(10px,-2px)}40%{opacity:0}55%{opacity:.8;transform:translate(-4px,1px)}75%{opacity:.9;transform:translate(7px,0)}90%,100%{opacity:0}}
@keyframes tear{0%,100%{opacity:0}10%{opacity:1;transform:translate(22px,0)}30%{opacity:1;transform:translate(-16px,0)}50%{opacity:0}65%{opacity:1;transform:translate(28px,0)}85%{opacity:1;transform:translate(-9px,0)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
""")


def qr_block(x: float, y: float) -> tuple[str, int]:
    """A scannable QR code at exactly 3px per module (whole pixels decode best)."""
    rows = [bytes(r) for r in segno.make(QR_URL, error="l").matrix]
    n, border, cell = len(rows), 2, 3
    size = (n + 2 * border) * cell
    runs = []
    for j, row in enumerate(rows):
        i = 0
        while i < n:
            if row[i]:
                k = i
                while k < n and row[k]:
                    k += 1
                runs.append(f"M{i + border} {j + border}h{k - i}v1h{i - k}z")
                i = k
            else:
                i += 1
    svg = (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="4" fill="{INK}"/>'
           f'<path transform="translate({x} {y}) scale({cell})" fill="{QR_DARK}" '
           f'shape-rendering="crispEdges" d="{"".join(runs)}"/>')
    return svg, size


def build() -> str:
    ts = Typesetter()

    face_size = 128
    face_top, face_bot = ts.extent(":(", face_size, "300")
    face_y = 34 - face_top                     # top of "(" at y=34
    face_mid = face_y + (face_top + face_bot) / 2

    y_name = face_y + face_bot + 50
    body, lh = 20, 30
    y_lines = [y_name + 36 + i * lh for i in range(len(LINES))]
    y_prog = y_lines[-1] + 44
    qr_y = round(y_prog + 26)
    qr, qr_size = qr_block(M, qr_y)
    assert qr_y + qr_size <= H - 16, "QR runs off the screen; shorten the copy or the URL"
    fine_x = M + qr_size + 22

    def face(**attrs: object) -> str:
        return ts.text(":(", M, face_y, face_size, "300", **attrs)

    rnd = random.Random(1432)
    specks = "".join(
        f'<circle cx="{rnd.uniform(10, W - 10):.1f}" cy="{rnd.uniform(10, H - 10):.1f}" '
        f'r="{rnd.uniform(.6, 1.5):.2f}" opacity="{rnd.uniform(.10, .26):.2f}"/>'
        for _ in range(40))

    frames = "".join(
        ts.text(f"{p}% complete", M, y_prog, body, "400", class_="fr", fill=INK,
                style=f"animation:on {dur}s linear {start}s")
        for p, start, dur in FRAMES)
    frames += ts.text("100% complete", M, y_prog, body, "400", class_="done", fill=INK)

    screen = "".join([
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#vig)"/>',
        f'<g fill="{INK}">{specks}</g>',
        face(class_="ga", fill=PINK),
        face(class_="gb", fill=CYAN),
        f'<g clip-path="url(#band)"><g class="tear">{face(fill=INK)}</g></g>',
        f'<g class="jit"><g class="sad">{face(fill=INK)}</g></g>',
        ts.text(":)", M, face_y, face_size, "300", class_="fix", fill=MINT),
        ts.text(NAME, M, y_name, 28, "700", fill=INK),
        "".join(ts.text(t, M, y, body, "400", fill=INK) for t, y in zip(LINES, y_lines)),
        frames,
        qr,
        ts.text(FINE, fine_x, qr_y + qr_size / 2 - 5, 14, "400", fill=INK_SOFT),
        ts.text(STOP, fine_x, qr_y + qr_size / 2 + 19, 15, "700", fill=INK),
        f'<rect class="flash" width="{W}" height="{H}" fill="{INK}"/>',
    ])

    css = CSS.substitute(fixed=FIXED, glitch=GLITCH, glen=f"{FIXED - GLITCH:.2f}", done=DONE)
    label = f"{NAME}. {' '.join(LINES)} {STOP}. A sad face on a blue screen glitches into a smile."
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{label}">'
        f"<title>{NAME}</title>"
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{BLUE_HI}"/><stop offset="1" stop-color="{BLUE_LO}"/></linearGradient>'
        '<radialGradient id="vig" cx=".28" cy=".22" r=".95">'
        '<stop offset="0" stop-color="#fff" stop-opacity=".10"/>'
        '<stop offset=".55" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000" stop-opacity=".22"/></radialGradient>'
        f'<clipPath id="screen"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
        f'<clipPath id="band"><rect y="{face_mid - 12:.1f}" width="{W}" height="22"/></clipPath>'
        f"{ts.defs()}</defs>"
        f"<style>{css}</style>"
        f'<g clip-path="url(#screen)">{screen}</g>'
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21.5" fill="none" '
        'stroke="#fff" stroke-opacity=".14" stroke-width="1.5"/>'
        "</svg>")


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")
