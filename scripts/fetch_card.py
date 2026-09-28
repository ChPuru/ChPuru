#!/usr/bin/env python3
"""Render assets/fetch.svg, a system report in the layout of hemfetch.

hemfetch is the system reporter inside hematite, the OS in
github.com/ChPuru/hematite. This card reuses its crystal logo, its 16-colour
palette and its layout: logo on the left, `label:` fields on the right, the
palette strip last.

.github/workflows/fetch.yml runs this daily, so the repo count, recent
languages and latest push stay current. Standard library only.

    python3 scripts/fetch_card.py                       # live, uses $GITHUB_TOKEN if set
    python3 scripts/fetch_card.py --fixture data.json   # offline test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgtype import Typesetter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("GITHUB_REPOSITORY_OWNER") or "ChPuru"

# ---- edit me ---------------------------------------------------------------
HOST = "hematite"
TOP = [
    ("os", "arch linux, nixos"),
    ("wm", "hyprland"),
    ("shell", "zsh + starship"),
    ("editor", "neovim"),
]
BOTTOM = [
    ("focus", "systems, backend, infrastructure"),
    ("status", "open to swe internships"),
]
RECENT_DAYS = 90  # "lately" = languages of repos pushed within this window
SKIP_LANGS = {"HTML", "CSS", "SCSS", "Jupyter Notebook", "TeX", "Makefile",
              "Dockerfile", "Batchfile", "PowerShell", "Procfile"}
SHORT = {"TypeScript": "ts", "JavaScript": "js"}
# ----------------------------------------------------------------------------

# hematite's logo and palette, exactly as hemfetch draws them
# (user/fetchinfo/src/lib.rs and user/term/src/main.rs in the hematite repo)
LOGO = [
    r"        /\        ",
    r"       /##\       ",
    r"      /####\      ",
    r"     /######\     ",
    r"    /###/\###\    ",
    r"   /###/  \###\   ",
    r"  /###/ /\ \###\  ",
    r"  \###\ \/ /###/  ",
    r"   \###\  /###/   ",
    r"    \###\/###/    ",
    r"     \######/     ",
    r"      \____/      ",
]
LOGO_SPLIT = 7  # rows above this are bright red, the rest dark red
PALETTE = ["#1a1e24", "#c05a5a", "#6fa86f", "#c8a85a", "#5a7ec0", "#a86fa8", "#5aa8a8", "#b8bcc0",
           "#5a6068", "#e86a6a", "#8ad08a", "#e8cc7a", "#7a9ee8", "#cc8acc", "#7acccc", "#e8ecf0"]
BG, FG, BORDER = "#101418", "#d0d8d0", "#2a3038"
DIM, RED, DARK_RED, GREEN, BLUE = PALETTE[8], PALETTE[9], PALETTE[1], PALETTE[10], PALETTE[12]
W = 840

CSS = (".cur{animation:blink 1.1s steps(1,end) infinite}"
       "@keyframes blink{50%{opacity:0}}"
       "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")

LangLookup = Callable[[str], Optional[dict]]


def when(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def ago(then: datetime, now: datetime) -> str:
    hours = (now - then).total_seconds() / 3600
    if hours < 1:
        return "just now"
    if hours < 24:
        return f"{int(hours)}h ago"
    days = int(hours // 24)
    if days == 1:
        return "yesterday"
    if days < 14:
        return f"{days} days ago"
    if days < 60:
        return f"{days // 7} weeks ago"
    return f"{days // 30} months ago"


def api(path: str):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"{USER}-fetch-card",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def load_live() -> tuple[dict, list[dict], LangLookup]:
    user = api(f"/users/{USER}")
    repos: list[dict] = []
    page = 1
    while True:
        batch = api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    return user, repos, lambda name: api(f"/repos/{USER}/{name}/languages")


def summarize(user: dict, repos: list[dict], languages_for: LangLookup, now: datetime) -> dict:
    own = [r for r in repos if not r.get("fork") and r["name"].lower() != USER.lower()]
    recent = [r for r in own if (now - when(r["pushed_at"])).days <= RECENT_DAYS] or own

    totals: Counter = Counter()
    by_bytes = True
    try:
        for r in recent:
            langs = languages_for(r["name"])
            if langs is None:
                raise LookupError(f"no language data for {r['name']}")
            for lang, size in langs.items():
                if lang not in SKIP_LANGS:
                    totals[lang] += size
    except (OSError, LookupError, ValueError) as err:  # urllib errors are OSErrors
        print(f"language bytes unavailable ({err}); counting primary languages", file=sys.stderr)
        totals = Counter(r["language"] for r in recent
                         if r.get("language") and r["language"] not in SKIP_LANGS)
        by_bytes = False

    def name(lang: str) -> str:
        return SHORT.get(lang, lang.lower())

    top = totals.most_common(4)
    if not top:
        lately = "nothing yet"
    elif by_bytes:
        total = sum(totals.values())
        lately = "  ".join(f"{name(l)} {max(1, round(100 * n / total))}%" for l, n in top)
    else:
        lately = "  ".join(f"{name(l)} ×{n}" for l, n in top)

    latest = max(own, key=lambda r: r["pushed_at"]) if own else None
    return {
        "repos": f"{user.get('public_repos', len(repos))} public",
        "lately": lately,
        "latest": f"{latest['name'].lower()}, {ago(when(latest['pushed_at']), now)}" if latest else "-",
    }


def render(facts: dict, ts: Typesetter) -> str:
    fs, lh, pad = 15, 22, 28
    cw = ts.char_width("M", fs)
    x0 = pad + 8
    info_x = x0 + (len(LOGO[0]) + 3) * cw
    label_w = 10
    max_value = int((W - pad - 8 - info_x) // cw) - label_w
    arrow = "❯" if ts.has("❯") else ">"
    parts: list[str] = []

    def spans(row: list[tuple[str, str, str]], x: float, y: float) -> None:
        for text, color, weight in row:
            parts.append(ts.text(text, x, y, fs, weight, fill=color))
            x += ts.width(text, fs)

    def field(label: str, value: str, color: str = FG) -> list[tuple[str, str, str]]:
        if len(value) > max_value:
            value = value[: max_value - 1] + "…"
        return [(f"{label}:".ljust(label_w), RED, "700"), (value, color, "400")]

    prompt = [("~", BLUE, "700"), (f" {arrow} ", GREEN, "700")]
    y = pad + fs
    spans(prompt + [("hemfetch", FG, "400")], x0, y)

    top = y + lh * 1.7
    for i, row in enumerate(LOGO):
        parts.append(ts.text(row, x0, top + i * lh, fs, "700",
                             fill=RED if i < LOGO_SPLIT else DARK_RED))

    title = f"purunjay@{HOST}"
    info = [[("purunjay", RED, "700"), ("@", DIM, "400"), (HOST, RED, "700")],
            [("-" * len(title), DIM, "400")]]
    info += [field(k, v) for k, v in TOP]
    info += [field("repos", facts["repos"]), field("lately", facts["lately"]),
             field("latest", facts["latest"], BLUE)]
    info += [field(k, v, GREEN if k == "status" else FG) for k, v in BOTTOM]
    for i, row in enumerate(info):
        spans(row, info_x, top + i * lh)

    # palette strip: two rows of eight "###" blocks after a blank line, as hemfetch prints it
    for r in range(2):
        for c in range(8):
            yb = top + (len(info) + 1 + r) * lh - fs * 0.8
            parts.append(f'<rect x="{info_x + 3 * c * cw:.1f}" y="{yb:.1f}" width="{3 * cw - 1:.1f}" '
                         f'height="{fs * 1.05:.1f}" fill="{PALETTE[r * 8 + c]}"/>')

    rows = max(len(LOGO), len(info) + 3)
    y_end = top + (rows - 1) * lh + lh * 1.7
    spans(prompt, x0, y_end)
    cur_x = x0 + ts.width(f"~ {arrow} ", fs)
    parts.append(f'<rect class="cur" x="{cur_x:.1f}" y="{y_end - fs * 0.8:.1f}" '
                 f'width="{cw * 0.62:.1f}" height="{fs:.1f}" fill="{FG}"/>')
    height = round(y_end + pad)

    body = "".join(parts)
    label = ("System report for purunjay: " + "; ".join(f"{k} {v}" for k, v in TOP)
             + f"; repos {facts['repos']}; lately {facts['lately']}; latest {facts['latest']}; "
             + "; ".join(f"{k} {v}" for k, v in BOTTOM))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-label="{label}">'
        f"<title>purunjay@{HOST}</title><defs>{ts.defs()}</defs><style>{CSS}</style>"
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{height - 1.5}" rx="12" fill="{BG}" '
        f'stroke="{BORDER}" stroke-width="1.5"/>'
        f"{body}</svg>")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture", help="JSON with user, repos and optional languages (offline test)")
    ap.add_argument("--now", help="ISO timestamp to treat as now (tests)")
    ap.add_argument("--out", default=str(ROOT / "assets" / "fetch.svg"))
    args = ap.parse_args()

    for row in LOGO:
        assert len(row) == len(LOGO[0]), "logo rows must be the same width"

    now = when(args.now) if args.now else datetime.now(timezone.utc)
    if args.fixture:
        data = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
        langs = data.get("languages")
        user, repos = data["user"], data["repos"]
        lookup: LangLookup = (lambda n: langs.get(n)) if langs else (lambda n: None)
    else:
        user, repos, lookup = load_live()

    facts = summarize(user, repos, lookup, now)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(facts, Typesetter()), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB): {facts}")


if __name__ == "__main__":
    main()
