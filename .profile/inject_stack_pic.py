import base64
import io
import os
import random
import re
import urllib.request
from PIL import Image

PIC_PATH = "assets/daily-pic.png"
ALBUM_URL = "https://ibb.co/album/6R58df"
MARKER = 'id="daily-pic-embed"'


def fetch_daily_pic():
    page = urllib.request.urlopen(ALBUM_URL, timeout=15).read().decode("utf-8", "ignore")
    imgs = sorted(set(re.findall(r'https://i\.ibb\.co/[^"]+\.(?:webp|png|jpg|gif)', page)))
    if not imgs:
        raise RuntimeError("No images found in ImgBB album")
    url = random.choice(imgs)
    urllib.request.urlretrieve(url, "raw_pic")
    im = Image.open("raw_pic").convert("RGBA")
    m = min(im.size)
    left = (im.width - m) // 2
    top = (im.height - m) // 2
    im = im.crop((left, top, left + m, top + m)).resize((500, 500), Image.Resampling.LANCZOS)
    os.makedirs("assets", exist_ok=True)
    im.save(PIC_PATH, "PNG", optimize=True)
    os.remove("raw_pic")


def inject_into_svg(svg_path, b64_uri):
    if not os.path.exists(svg_path):
        return
    s = open(svg_path, "r", encoding="utf-8").read()
    # Remove previous injection if present
    s = re.sub(r'<g id="daily-pic-embed">.*?</g>', "", s, flags=re.S)

    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', s)
    if not m:
        return
    W = float(m.group(1))
    H = float(m.group(2))

    # Place rounded photo on the right side of the Stack card
    size = min(244.0, H - 56.0)
    x = W - 28.0 - size
    y = (H - size) / 2.0
    r = 26.0

    # Unique clip id per file
    cid = "dpClip_" + ("d" if "dark" in svg_path else "l")
    block = (
        f'<g {MARKER}>'
        f'<defs><clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{r:.1f}"/></clipPath></defs>'
        f'<image href="{b64_uri}" x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" clip-path="url(#{cid})" preserveAspectRatio="xMidYMid slice"/>'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{r:.1f}" fill="none" stroke="currentColor" stroke-opacity="0.16" stroke-width="1.5"/>'
        f'</g>'
    )
    s = s.replace("</svg>", block + "</svg>")
    open(svg_path, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    import sys
    if "--fetch" in sys.argv or not os.path.exists(PIC_PATH):
        fetch_daily_pic()
    raw = open(PIC_PATH, "rb").read()
    b64 = "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
    for p in ("assets/stack-dark.svg", "assets/stack-light.svg"):
        inject_into_svg(p, b64)
    for hp in ("assets/hero-dark.svg", "assets/hero-light.svg"):
        if os.path.exists(hp):
            hs = open(hp, "r", encoding="utf-8").read()
            hs = re.sub(r'<path d="[^"]+" fill="[^"]+" opacity="\.9"/>(?=<clipPath id="ava">)', "", hs)
            open(hp, "w", encoding="utf-8").write(hs)
    print("Injected daily-pic into stack SVGs & cleaned avatar halo")
