"""Build assets/apps/<name>.svg: app icons trimmed and styled as Liquid Glass tiles.

Usage: python3 scripts/gen_icons.py assets/apps  (needs dwebp from the webp package)
"""
import base64, math, os, subprocess, sys, tempfile, urllib.request

OUT = sys.argv[1]
NAMES = ["notchpal", "notchpal-android", "barqr", "morse", "mirrorme", "splice", "droidtransfer", "diskkeeper", "wasthu"]
BASE = "https://hexhad.github.io/src/products/{}-icon.webp"
SIZE = 112


def read_pam(path):
    data = open(path, "rb").read()
    header, _, rest = data.partition(b"ENDHDR\n")
    h = dict(l.split(b" ", 1) for l in header.splitlines()[1:] if b" " in l)
    return int(h[b"WIDTH"]), int(h[b"HEIGHT"]), rest


def bbox(w, h, px):
    xs, ys = [], []
    for y in range(h):
        row = px[y * w * 4:(y + 1) * w * 4]
        for x in range(w):
            if row[x * 4 + 3] > 24:
                xs.append(x); ys.append(y)
                break
        for x in range(w - 1, -1, -1):
            if row[x * 4 + 3] > 24:
                xs.append(x)
                break
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def squircle(x, y, s, n=5.0, steps=96):
    """Superellipse path, close to Apple's continuous-corner icon shape."""
    pts = []
    for i in range(steps):
        a = 2 * math.pi * i / steps
        c, si = math.cos(a), math.sin(a)
        px = math.copysign(abs(c) ** (2 / n), c)
        py = math.copysign(abs(si) ** (2 / n), si)
        pts.append(f"{x + s / 2 + px * s / 2:.2f},{y + s / 2 + py * s / 2:.2f}")
    return "M" + " L".join(pts) + "Z"


def glass_svg(vx, vy, side, w, h, b64):
    """Liquid Glass style (web approximation, not Apple's material): squircle,
    specular rim, soft top gloss and a floating shadow."""
    pad = side * 0.1
    path = squircle(vx, vy, side)
    sw = side * 0.014
    inner = squircle(vx + sw / 2, vy + sw / 2, side - sw)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{SIZE}" height="{SIZE}" viewBox="{vx - pad:.1f} {vy - pad:.1f} {side + 2 * pad:.1f} {side + 2 * pad:.1f}">'
        f'<defs>'
        f'<clipPath id="c"><path d="{path}"/></clipPath>'
        f'<filter id="sh" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feDropShadow dx="0" dy="{side * 0.035:.1f}" stdDeviation="{side * 0.045:.1f}" flood-color="#000" flood-opacity=".38"/></filter>'
        f'<linearGradient id="gl" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#000" stop-opacity=".12"/></linearGradient>'
        f'<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset=".35" stop-color="#fff" stop-opacity=".08"/>'
        f'<stop offset=".7" stop-color="#fff" stop-opacity=".04"/><stop offset="1" stop-color="#fff" stop-opacity=".4"/></linearGradient>'
        f'</defs>'
        f'<path d="{path}" fill="#0A0B0D" filter="url(#sh)"/>'
        f'<g clip-path="url(#c)">'
        f'<image width="{w}" height="{h}" xlink:href="data:image/webp;base64,{b64}" href="data:image/webp;base64,{b64}"/>'
        f'<rect x="{vx}" y="{vy}" width="{side}" height="{side}" fill="url(#gl)"/>'
        f'</g>'
        f'<path d="{inner}" fill="none" stroke="url(#rim)" stroke-width="{sw:.2f}"/>'
        f'</svg>\n')


os.makedirs(OUT, exist_ok=True)
tmp = tempfile.mkdtemp()
for n in NAMES:
    webp = urllib.request.urlopen(BASE.format(n)).read()
    src, pam = os.path.join(tmp, n + ".webp"), os.path.join(tmp, n + ".pam")
    open(src, "wb").write(webp)
    subprocess.run(["dwebp", "-quiet", "-pam", src, "-o", pam], check=True)
    w, h, px = read_pam(pam)
    x0, y0, x1, y1 = bbox(w, h, px)
    side = max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    vx, vy = cx - side / 2, cy - side / 2
    b64 = base64.b64encode(webp).decode()
    svg = glass_svg(vx, vy, side, w, h, b64)
    open(os.path.join(OUT, n + ".svg"), "w").write(svg)
    print(f"{n:18} {w}x{h} content {x1 - x0}x{y1 - y0} -> {len(svg) // 1024} KB")
