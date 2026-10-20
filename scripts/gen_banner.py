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

W, H = 1200, 340
MINT, BG, LABEL, LABEL2 = "#43E0A0", "#0A0B0D", "#EDEDEF", "#9BA1A8"

# --- timeline -----------------------------------------------------------------
# One loop: the runner enters from the left edge running along the top of the
# headline, stops at its end and looks at the mark (the mark flashes back),
# hops down to the lane at the bottom and sprints off the right edge.
CYCLE = 12.0                 # seconds per loop
BASE_1, BASE_2, BASE_S = 214, 266, 304   # headline and tagline baselines
PLAT = BASE_1 - 33           # top of the headline's tallest letters
GROUND = 330                 # bottom lane
X_IN, X_STOP, X_LAND, X_OUT = -90, 345, 560, 1230   # sprite left edge
T_STOP, T_GO, T_LAND = 30, 45, 53                   # % of the loop
REACT = 34                   # % when the mark flashes back
MARK_X, MARK_Y = 940, 52


def feet_pct(x):
    """% of the loop when the sprite's left edge reaches x on the bottom lane."""
    return T_LAND + (x - X_LAND) / (X_OUT - X_LAND) * (100 - T_LAND)


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
        lit = ""
        if abs(cy - GROUND) < dy * 0.75 and X_LAND + 40 <= cx <= min(X_OUT, W) + 40:
            # light the cell when the runner's feet pass over it
            pct = feet_pct(cx - 40)
            lit = f' class="lit" style="animation-delay:{CYCLE * pct / 100:.2f}s"'
        hexes.append(f'<polygon points="{pts}"{lit}/>')

# --- pixel runner sprite sheet ---------------------------------------------
# A 20x24 pixel developer: dark hair, beard, mint headset and hoodie, phone in
# hand. Limbs are posed from joint angles so the 8-frame stride reads cleanly.
P = 4
GW, GH = 20, 24
FW, FH = GW * P, GH * P
PAL = {
    "o": "#06070A",  # outline
    "h": "#2B2420",  # hair
    "s": "#E6B089",  # skin
    "S": "#C98E68",  # skin shade
    "b": "#3B2C24",  # beard
    "e": "#0A0B0D",  # eye
    "m": MINT,       # hoodie
    "M": "#2DBF85",  # hoodie shade
    "d": "#0A7A52",  # hoodie deep shade / back arm
    "w": "#EDEDEF",  # strings, shoe
    "g": "#3A4048",  # trousers
    "G": "#2A2F36",  # trousers back leg
    "p": "#1A1D21",  # phone body
    "q": "#9FF5D0",  # phone screen glow
}
HEAD = [
    ".......hhhhh........",
    "......hhhhhhhh......",
    ".....hhhhhhhhhh.....",
    ".....hhhhhhhsss.....",
    ".....hmhsssssess....",
    ".....mmhSsssssss....",
    ".....hmhbsssbbbs....",
    "......hbbbbbbbb.....",
    ".......bbbbbbb......",
    "........SSS.........",
]
TORSO = [
    ".......mmmmmmm......",
    "......mmmmmwmmm.....",
    "......MmmmmwmmM.....",
    "......MmmmmmmmM.....",
    "......MMmmmmmmM.....",
    ".......MMMMMMM......",
]
HIP = (9.5, 16)
SHOULDER = (10.5, 11)
THIGH = [38, 14, -10, -34, -22, 4, 26, 40]      # degrees from vertical, + is forward
KNEE = [12, 18, 22, 30, 95, 105, 75, 35]        # shin bend behind the thigh
BOB = [0, 1, 1, 0, -1, 0, 0, -1]


def put(grid, x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < GW and 0 <= y < GH:
        grid[y][x] = c


def limb(grid, x, y, ang, length, c, thick=2):
    rad = math.radians(ang)
    ex, ey = x + math.sin(rad) * length, y + math.cos(rad) * length
    for k in range(int(length * 4) + 1):
        t = k / (length * 4)
        px, py = x + (ex - x) * t, y + (ey - y) * t
        for j in range(thick):
            put(grid, px + j - (thick - 1) / 2, py, c)
    return ex, ey


def leg(grid, thigh, knee, c):
    kx, ky = limb(grid, *HIP, thigh, 4, c)
    fx, fy = limb(grid, kx, ky, thigh - knee, 4, c)
    for dx in range(3):  # shoe points forward
        put(grid, fx + dx - 0.5, fy + 0.5, "w")


def arm(grid, swing, fore, upper_c, phone=False):
    ex, ey = limb(grid, *SHOULDER, swing, 3.2, upper_c)
    hx, hy = limb(grid, ex, ey, fore, 3, upper_c)
    put(grid, hx, hy, "s")
    if phone:
        for dy in range(3):
            put(grid, hx + 1, hy - 1 + dy, "p")
        put(grid, hx + 1, hy, "q")


def outline(grid):
    out = [row[:] for row in grid]
    for y in range(GH):
        for x in range(GW):
            if grid[y][x] != ".":
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < GW and 0 <= ny < GH and grid[ny][nx] != ".":
                    out[y][x] = "o"
                    break
    return out


def pose(back_leg, front_leg, back_arm, front_arm, head=HEAD):
    g = [["."] * GW for _ in range(GH)]
    leg(g, *back_leg, "G")
    arm(g, *back_arm, "d")
    for y, r in enumerate(TORSO):
        for x, c in enumerate(r):
            if c != ".":
                g[y + len(head)][x] = c
    for y, r in enumerate(head):
        for x, c in enumerate(r):
            if c != ".":
                g[y][x] = c
    leg(g, *front_leg, "g")
    arm(g, *front_arm, "M", phone=True)
    return g


def rects(g, ox, bob):
    g = outline(g)
    out = []
    for y, r in enumerate(g):
        x = 0
        while x < GW:
            c, run = r[x], 1
            while x + run < GW and r[x + run] == c:
                run += 1
            if c in PAL:
                out.append(f'<rect x="{ox + x * P}" y="{(y + 1 + bob) * P}" width="{run * P}" height="{P}" fill="{PAL[c]}"/>')
            x += run
    return "".join(out)


def run_frame(i):
    j = (i + 4) % 8
    return rects(pose((THIGH[j], KNEE[j]), (THIGH[i], KNEE[i]),
                      (-THIGH[j] * 0.9, -THIGH[j] * 0.9 + 100), (-THIGH[i] * 0.9, -THIGH[i] * 0.9 + 100)),
                 i * FW, BOB[i])


# Standing still, head tilted up, phone raised toward the mark.
HEAD_UP = [r for r in HEAD]
HEAD_UP[3] = ".....hhhhhhhsses...."
HEAD_UP[4] = ".....hmhsssssssss..."
look = rects(pose((-5, 0), (6, 0), (-12, 20), (140, 175), HEAD_UP), 0, 0)
# a small mint "!" above the head
bang = "".join(f'<rect x="{15 * P}" y="{y * P}" width="{P}" height="{P}" fill="{MINT}"/>' for y in (-6, -5, -4, -2))


sheet = "".join(run_frame(i) for i in range(8))
SHEET_W = 8 * FW

# --- HEXHAD mark (from src/brand/hexhad-mark.svg, 100x100) -----------------
MARK_HEX = "M53.03 7.25L85.51 26.00Q88.54 27.75 88.54 31.25L88.54 68.75Q88.54 72.25 85.51 74.00L53.03 92.75Q50.00 94.50 46.97 92.75L14.49 74.00Q11.46 72.25 11.46 68.75L11.46 31.25Q11.46 27.75 14.49 26.00L46.97 7.25Q50.00 5.50 53.03 7.25Z"
MARK_H = "M30.04 35.00L36.96 31.00Q38.00 30.40 38.00 31.60L38.00 43.30Q38.00 44.50 39.04 45.10L48.96 50.83Q50.00 51.43 51.04 50.83L60.96 45.10Q62.00 44.50 62.00 43.30L62.00 31.60Q62.00 30.40 63.04 31.00L69.96 35.00Q71.00 35.60 71.00 36.80L71.00 63.20Q71.00 64.400 69.96 65.00L63.04 69.00Q62.00 69.60 62.00 68.40L62.00 55.90Q62.00 54.70 60.96 55.30L51.04 61.03Q50.00 61.63 48.96 61.03L39.04 55.30Q38.00 54.70 38.00 55.90L38.00 68.40Q38.00 69.60 36.96 69.00L30.04 65.00Q29.00 64.40 29.00 63.20L29.00 36.80Q29.00 35.60 30.04 35.00Z"


def mark(x, y, size, stroke=6, color=LABEL):
    s = size / 100
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="{MARK_HEX}" fill="none" stroke="{color}" stroke-width="{stroke}"/>'
            f'<path d="{MARK_H}" fill="{color}"/></g>')


PLAT_Y = PLAT - FH + 2      # feet on the headline
RUN_Y = GROUND - FH + 2     # feet on the bottom lane
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="HEXHAD. Tools for people who ship apps.">
<title>HEXHAD. Tools for people who ship apps.</title>
<defs>
<style>
@font-face{{font-family:G;font-weight:650;src:url(data:font/woff2;base64,{geist}) format("woff2")}}
@font-face{{font-family:M;src:url(data:font/woff2;base64,{mono}) format("woff2")}}
.h{{font:650 46px G,ui-sans-serif,system-ui,sans-serif;letter-spacing:-1.6px;fill:{LABEL}}}
.w{{font:650 17px G,ui-sans-serif,system-ui,sans-serif;letter-spacing:2.4px;fill:{LABEL}}}
.s{{font:400 14px M,ui-monospace,monospace;fill:{LABEL2}}}
.sheet{{animation:run .72s steps(8) infinite}}
.trip{{animation:trip {CYCLE}s linear infinite}}
.hex polygon{{fill:{MINT};fill-opacity:0;stroke:{MINT};stroke-opacity:.09;stroke-width:1}}
.hex .lit{{animation:lit {CYCLE}s ease-out infinite backwards}}
.runner{{animation:runv {CYCLE}s infinite}}
.looker{{opacity:0;animation:lookv {CYCLE}s infinite}}
.pop,.ring,.flash,.bang{{transform-box:fill-box;transform-origin:center}}
.bang{{animation:bang {CYCLE}s infinite}}
.pop{{animation:pop {CYCLE}s infinite}}
.flash{{opacity:0;animation:flash {CYCLE}s infinite}}
.ring{{opacity:0;animation:ring {CYCLE}s cubic-bezier(.16,1,.3,1) infinite}}
@keyframes run{{to{{transform:translateX(-{SHEET_W}px)}}}}
@keyframes trip{{
0%{{transform:translate({X_IN}px,{PLAT_Y}px)}}
{T_STOP}%,{T_GO}%{{transform:translate({X_STOP}px,{PLAT_Y}px);animation-timing-function:cubic-bezier(.2,.6,.4,1)}}
{(T_GO + T_LAND) / 2}%{{transform:translate({(X_STOP + X_LAND) / 2}px,{PLAT_Y - 46}px);animation-timing-function:cubic-bezier(.6,0,.8,.4)}}
{T_LAND}%{{transform:translate({X_LAND}px,{RUN_Y}px)}}
100%{{transform:translate({X_OUT}px,{RUN_Y}px)}}}}
@keyframes runv{{0%,{T_STOP - .01}%{{opacity:1}}{T_STOP}%,{T_GO - .01}%{{opacity:0}}{T_GO}%,100%{{opacity:1}}}}
@keyframes lookv{{0%,{T_STOP - .01}%{{opacity:0}}{T_STOP}%,{T_GO - .01}%{{opacity:1}}{T_GO}%,100%{{opacity:0}}}}
@keyframes bang{{0%,{REACT - 3}%{{transform:scale(0)}}{REACT - 1}%{{transform:scale(1.3)}}{REACT + 1}%,{T_GO - 3}%{{transform:scale(1)}}{T_GO - 1}%,100%{{transform:scale(0)}}}}
@keyframes lit{{0%{{fill-opacity:0;stroke-opacity:.09}}3%{{fill-opacity:.28;stroke-opacity:.6}}18%,100%{{fill-opacity:0;stroke-opacity:.09}}}}
@keyframes pop{{0%,{REACT - 1}%,100%{{transform:scale(1)}}{REACT + 3}%{{transform:scale(1.07)}}{REACT + 12}%{{transform:scale(1)}}}}
@keyframes flash{{0%,{REACT - 1}%,100%{{opacity:0}}{REACT + 2}%{{opacity:1}}{REACT + 20}%{{opacity:0}}}}
@keyframes ring{{0%,{REACT - 1}%{{opacity:0;transform:scale(1)}}{REACT}%{{opacity:.7;transform:scale(1)}}{REACT + 22}%,100%{{opacity:0;transform:scale(1.6)}}}}
@media (prefers-reduced-motion:reduce){{.sheet,.trip,.lit,.pop,.flash,.ring,.runner,.looker,.bang{{animation:none}}.trip{{transform:translate({X_STOP}px,{PLAT_Y}px)}}.runner{{opacity:0}}.looker{{opacity:1}}}}
</style>
<radialGradient id="glow" cx="78%" cy="45%" r="45%"><stop offset="0" stop-color="{MINT}" stop-opacity=".22"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" x2="1"><stop offset=".42" stop-color="#fff" stop-opacity="0"/><stop offset=".62" stop-color="#fff"/></linearGradient>
<mask id="fm"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>

<clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<clipPath id="win"><rect width="{FW}" height="{FH + 2 * P}"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
<g class="hex" mask="url(#fm)">{"".join(hexes)}</g>
<g transform="translate({MARK_X} {MARK_Y}) scale(1.72)"><path class="ring" d="{MARK_HEX}" fill="none" stroke="{MINT}" stroke-width="3"/></g>
<g class="pop">{mark(MARK_X, MARK_Y, 172, 6)}<g class="flash">{mark(MARK_X, MARK_Y, 172, 6, MINT)}</g></g>
<line x1="560" y1="{GROUND + 4}" x2="{W}" y2="{GROUND + 4}" stroke="{MINT}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="4 6" mask="url(#fm)"/>
</g>
{mark(64, 36, 30, 7)}
<text x="104" y="58" class="w">{WORD}</text>
<text x="64" y="{BASE_1}" class="h">{HEAD_1}</text>
<text x="64" y="{BASE_2}" class="h">{HEAD_2a}<tspan fill="{MINT}">{HEAD_2b}</tspan></text>
<text x="64" y="{BASE_S}" class="s">{SUB}</text>
<g clip-path="url(#card)"><g class="trip"><g class="runner" clip-path="url(#win)"><g class="sheet">{sheet}</g></g><g class="looker">{look}<g class="bang">{bang}</g></g></g></g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="23.5" fill="none" stroke="#fff" stroke-opacity=".08"/>
</svg>
'''
open(OUT, "w").write(svg)
print(f"wrote {OUT}: {len(svg) / 1024:.1f} KB")
