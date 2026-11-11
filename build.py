"""Build the standalone Quick Math site into docs/ (served by GitHub Pages).

index.html is the source of truth and is also what gets published as the
claude.ai artifact (which supplies its own <html>/<head> wrapper). This script
wraps it in a full document, adds home-screen app metadata, and draws the icons.

Usage:  py build.py
"""
from pathlib import Path
import json
import re

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
OUT = ROOT / "docs"

ACCENT = (45, 85, 224)      # --accent (light theme)
WHITE = (255, 255, 255)
HI = (244, 185, 26)         # --hi

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Quick Math</title>
<meta name="description" content="Quick mental math drills: addition, subtraction, multiplication and division.">
<meta name="theme-color" content="#EDF0F6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E1422" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Quick Math">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" type="image/png" href="icon-192.png">
<link rel="manifest" href="manifest.webmanifest">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
"""


def build_html() -> str:
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    # Everything before the first <style> is title/meta/link lines meant for the
    # artifact; keep the font links, drop the rest (HEAD above replaces them).
    head_part, rest = src.split("<style>", 1)
    fonts = "\n".join(line for line in head_part.splitlines()
                      if line.startswith("<link") and "fonts." in line)
    style, body = ("<style>" + rest).split("</style>", 1)
    return f"{HEAD}{fonts}\n{style}</style>\n</head>\n<body>{body.rstrip()}\n</body>\n</html>\n"


def draw_icon(size: int, maskable: bool = False) -> Image.Image:
    """Blue tile with + − × ÷ in a 2x2 grid; the × sits on a yellow chip."""
    s = 4  # supersample for smooth edges
    n = size * s
    img = Image.new("RGB", (n, n), ACCENT)
    d = ImageDraw.Draw(img)
    pad = n * (0.22 if maskable else 0.16)
    cell = (n - 2 * pad) / 2
    w = round(n * 0.055)          # stroke width
    r = cell * 0.26               # half-length of each symbol

    def centre(col, row):
        return pad + cell * (col + 0.5), pad + cell * (row + 0.5)

    def line(x1, y1, x2, y2, color=WHITE):
        d.line((x1, y1, x2, y2), fill=color, width=w)
        for x, y in ((x1, y1), (x2, y2)):   # round caps
            d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=color)

    cx, cy = centre(0, 0)            # +
    line(cx - r, cy, cx + r, cy); line(cx, cy - r, cx, cy + r)
    cx, cy = centre(1, 0)            # −
    line(cx - r, cy, cx + r, cy)
    cx, cy = centre(0, 1)            # × on a yellow chip
    c = r * 1.55
    d.rounded_rectangle((cx - c, cy - c, cx + c, cy + c), radius=c * 0.35, fill=HI)
    k = r * 0.78
    line(cx - k, cy - k, cx + k, cy + k, ACCENT); line(cx - k, cy + k, cx + k, cy - k, ACCENT)
    cx, cy = centre(1, 1)            # ÷
    line(cx - r, cy, cx + r, cy)
    dot = w * 0.85
    for dy in (-r * 0.62, r * 0.62):
        d.ellipse((cx - dot, cy + dy - dot, cx + dot, cy + dy + dot), fill=WHITE)
    return img.resize((size, size), Image.LANCZOS)


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(build_html(), encoding="utf-8")
    for size in (180, 192, 512):
        draw_icon(size).save(OUT / f"icon-{size}.png", optimize=True)
    draw_icon(512, maskable=True).save(OUT / "icon-maskable-512.png", optimize=True)
    manifest = {
        "name": "Quick Math",
        "short_name": "Quick Math",
        "description": "Quick mental math drills.",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#EDF0F6",
        "theme_color": "#2D55E0",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (OUT / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("Built", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
