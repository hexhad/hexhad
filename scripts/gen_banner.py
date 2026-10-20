"""Generate assets/banner.svg: compact HEXHAD banner with a CSS sprite-sheet runner.

Usage: python3 scripts/gen_banner.py assets/banner.svg
"""
import base64, math, re, sys, urllib.parse, urllib.request

OUT = sys.argv[1]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

HEAD_1, HEAD_2a, HEAD_2b = "Tools for people", "who ", "ship apps."
WORD = "HEXHAD"
SUB = "Mobile first. Android, iOS, macOS and Windows."


def font(family, text):
    q = urllib.parse.urlencode({"family": family, "text": text})
    css = urllib.request.urlopen(urllib.request.Request(
        "https://fonts.googleapis.com/css2?" + q, headers={"User-Agent": UA})).read().decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read()
    return base64.b64encode(data).decode()


geist = font("Geist:wght@650", HEAD_1 + HEAD_2a + HEAD_2b + WORD)
mono = font("Geist Mono:wght@400", SUB)

W, H = 1200, 300
MINT, BG, LABEL, LABEL2 = "#43E0A0", "#0A0B0D", "#EDEDEF", "#9BA1A8"

# --- hex cell field (pointy-top), right side only -------------------------
R = 22
hexes = []
dx, dy = math.sqrt(3) * R, 1.5 * R
for row in range(-1, int(H / dy) + 2):
    for col in range(-1, int(W / dx) + 2):
        cx = col * dx + (dx / 2 if row % 2 else 0)
        cy = row * dy
        if cx < 520:
            continue
        pts = " ".join(f"{cx + R * math.cos(math.radians(60 * i - 30)):.1f},{cy + R * math.sin(math.radians(60 * i - 30)):.1f}" for i in range(6))
        hexes.append(f'<polygon points="{pts}"/>')

# --- pixel runner sprite sheet ---------------------------------------------
# 16x16 grid per frame, P px per pixel. Palette: k outline, s skin, m mint cap/shirt, g graphite pants, w shoe
P = 5
FW = 16 * P
PAL = {"k": "#0A0B0D", "s": "#F2C9A0", "m": MINT, "d": "#0A7A52", "g": "#3A4048", "w": "#EDEDEF", "p": "#1A1D21"}

HEAD = [
    "......mmmm......",
    ".....mmmmmmd....",
    ".....ssss.......",
    ".....sksss......",
    ".....ssss.......",
]
TORSO = [
    "......mmm.......",
    ".....mmmmm......",
    ".....mmmmm......",
    "......ggg.......",
]

# Legs (rows 9..15) and arm offsets for 8 run frames: a simple stride cycle.
LEGS = [
    ["....gg..gg.....", "...gg....gg....", "..gg......gg...", ".ww........ww..", "................", "................", "................"],
    ["....gg.gg......", "...gg...gg.....", "...gg....gg....", "..ww.....ww....", "................", "................", "................"],
    [".....ggg.......", ".....gg.g......", ".....gg.gg.....", ".....ww.ww.....", "................", "................", "................"],
    [".....gg.g......", "......g.gg.....", "......g..gg....", ".....ww..ww....", "................", "................", "................"],
    ["....gg..gg.....", "...gg....gg....", "..gg......gg...", ".ww........ww..", "................", "................", "................"],
    ["......gggg.....", ".....gg..gg....", "....gg....gg...", "...ww.....ww...", "................", "................", "................"],
    [".....ggg.......", ".....g.gg......", ".....g..gg.....", "....ww..ww.....", "................", "................", "................"],
    [".....gg.g......", ".....gg..g.....", "....gg...gg....", "...ww....ww....", "................", "................", "................"],
]
# Arm swing: (back-arm col, front-arm col) on torso row 2; phone in front hand.
ARMS = [(3, 11), (4, 10), (5, 9), (4, 10), (11, 3), (10, 4), (9, 5), (10, 4)]
BOB = [0, 1, 1, 0, 0, 1, 1, 0]


def frame(i):
    rows = [list(r.ljust(16, ".")) for r in HEAD + TORSO]
    back, front = ARMS[i]
    rows[6][back] = "s"
    rows[7][front] = "s"
    rows[6][front] = "p"  # phone
    rows += [list(r.ljust(16, ".")) for r in LEGS[i][:4]]
    rects = []
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c in PAL:
                rects.append(f'<rect x="{i * FW + x * P}" y="{(y + BOB[i]) * P}" width="{P}" height="{P}" fill="{PAL[c]}"/>')
    return "".join(rects)


sheet = "".join(frame(i) for i in range(8))
SHEET_W = 8 * FW

# --- HEXHAD mark (from src/brand/hexhad-mark.svg, 100x100) -----------------
MARK_HEX = "M53.03 7.25L85.51 26.00Q88.54 27.75 88.54 31.25L88.54 68.75Q88.54 72.25 85.51 74.00L53.03 92.75Q50.00 94.50 46.97 92.75L14.49 74.00Q11.46 72.25 11.46 68.75L11.46 31.25Q11.46 27.75 14.49 26.00L46.97 7.25Q50.00 5.50 53.03 7.25Z"
MARK_H = "M30.04 35.00L36.96 31.00Q38.00 30.40 38.00 31.60L38.00 43.30Q38.00 44.50 39.04 45.10L48.96 50.83Q50.00 51.43 51.04 50.83L60.96 45.10Q62.00 44.50 62.00 43.30L62.00 31.60Q62.00 30.40 63.04 31.00L69.96 35.00Q71.00 35.60 71.00 36.80L71.00 63.20Q71.00 64.400 69.96 65.00L63.04 69.00Q62.00 69.60 62.00 68.40L62.00 55.90Q62.00 54.70 60.96 55.30L51.04 61.03Q50.00 61.63 48.96 61.03L39.04 55.30Q38.00 54.70 38.00 55.90L38.00 68.40Q38.00 69.60 36.96 69.00L30.04 65.00Q29.00 64.40 29.00 63.20L29.00 36.80Q29.00 35.60 30.04 35.00Z"


def mark(x, y, size, stroke=6):
    s = size / 100
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="{MARK_HEX}" fill="none" stroke="{LABEL}" stroke-width="{stroke}"/>'
            f'<path d="{MARK_H}" fill="{LABEL}"/></g>')


GROUND = 250
RUN_Y = GROUND - 16 * P + 4  # feet touch the ground line
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="HEXHAD. Tools for people who ship apps.">
<title>HEXHAD. Tools for people who ship apps.</title>
<defs>
<style>
@font-face{{font-family:G;font-weight:650;src:url(data:font/woff2;base64,{geist}) format("woff2")}}
@font-face{{font-family:M;src:url(data:font/woff2;base64,{mono}) format("woff2")}}
.h{{font:650 46px G,ui-sans-serif,system-ui,sans-serif;letter-spacing:-1.6px;fill:{LABEL}}}
.w{{font:650 17px G,ui-sans-serif,system-ui,sans-serif;letter-spacing:2.4px;fill:{LABEL}}}
.s{{font:400 14px M,ui-monospace,monospace;fill:{LABEL2}}}
.sheet{{animation:run .8s steps(8) infinite}}
.trip{{animation:trip 7s linear infinite}}
.hex polygon{{fill:none;stroke:{MINT};stroke-opacity:.09;stroke-width:1}}
@keyframes run{{to{{transform:translateX(-{SHEET_W}px)}}}}
@keyframes trip{{from{{transform:translateX(560px)}}to{{transform:translateX({W + 20}px)}}}}
@media (prefers-reduced-motion:reduce){{.sheet,.trip{{animation:none}}.trip{{transform:translateX(980px)}}}}
</style>
<radialGradient id="glow" cx="78%" cy="45%" r="45%"><stop offset="0" stop-color="{MINT}" stop-opacity=".22"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" x2="1"><stop offset=".42" stop-color="#fff" stop-opacity="0"/><stop offset=".62" stop-color="#fff"/></linearGradient>
<mask id="fm"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<clipPath id="win"><rect width="{FW}" height="{16 * P + P}"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
<g class="hex" mask="url(#fm)">{"".join(hexes)}</g>
{mark(940, 38, 172, 6)}
<line x1="560" y1="{GROUND + 4}" x2="{W}" y2="{GROUND + 4}" stroke="{MINT}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="4 6" mask="url(#fm)"/>
<g class="trip"><g transform="translate(0 {RUN_Y})"><g clip-path="url(#win)"><g class="sheet">{sheet}</g></g></g></g>
</g>
{mark(64, 70, 30, 7)}
<text x="104" y="92" class="w">{WORD}</text>
<text x="64" y="160" class="h">{HEAD_1}</text>
<text x="64" y="212" class="h">{HEAD_2a}<tspan fill="{MINT}">{HEAD_2b}</tspan></text>
<text x="64" y="252" class="s">{SUB}</text>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="23.5" fill="none" stroke="#fff" stroke-opacity=".08"/>
</svg>
'''
open(OUT, "w").write(svg)
print(f"wrote {OUT}: {len(svg) / 1024:.1f} KB")
