import base64
import io
import os
import random
import re
import urllib.request
from PIL import Image

PIC_PATH = "assets/daily-pic.png"
ALBUM_URL = "https://ibb.co/album/6R58df"
FALLBACK_URL = "https://avatars.githubusercontent.com/u/126146783?v=4"
MARKER = 'id="daily-pic-embed"'
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def download_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()


def fetch_daily_pic():
    raw_bytes = None
    try:
        page = download_bytes(ALBUM_URL).decode("utf-8", "ignore")
        imgs = list(set(re.findall(r'https://i\.ibb\.co/[^"]+\.(?:webp|png|jpg|gif)', page)))
        random.shuffle(imgs)
        for url in imgs[:5]:
            try:
                raw_bytes = download_bytes(url)
                print("Selected:", url)
                break
            except Exception as e:
                print("Skip", url, e)
    except Exception as e:
        print("Album fetch failed:", e)

    if raw_bytes is None:
        if os.path.exists(PIC_PATH):
            print("Keeping existing daily-pic.png")
            return
        print("Using GitHub avatar fallback")
        raw_bytes = download_bytes(FALLBACK_URL)

    with open("raw_pic", "wb") as f:
        f.write(raw_bytes)
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
    s = re.sub(r'<g id="daily-pic-embed">.*?</g>', "", s, flags=re.S)

    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', s)
    if not m:
        return
    W = float(m.group(1))
    H = float(m.group(2))

    size = min(332.0, H - 96.0)
    x = W - 48.0 - size
    y = (H - size) / 2.0
    r = 26.0

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
    av_bytes = None
    try:
        av_bytes = download_bytes(FALLBACK_URL)
    except Exception:
        if os.path.exists(".profile/avatar.png"):
            av_bytes = open(".profile/avatar.png", "rb").read()
    if av_bytes:
        av_im = Image.open(io.BytesIO(av_bytes)).convert("RGBA").resize((240, 240), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        av_im.save(buf, "PNG", optimize=True)
        av_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
        for hp in ("assets/hero-dark.svg", "assets/hero-light.svg"):
            if os.path.exists(hp):
                hs = open(hp, "r", encoding="utf-8").read()
                if "<image " in hs:
                    hs = re.sub(r'(<image[^>]*\bhref=")[^"]+(")', r'\g<1>' + av_b64 + r'\2', hs, count=1)
                    open(hp, "w", encoding="utf-8").write(hs)
                elif '<clipPath id="ava">' in hs and '<g class="up"' in hs:
                    img_tag = '<g class="fade"><image href="' + av_b64 + '" x="50" y="50" width="200" height="200" clip-path="url(#ava)" preserveAspectRatio="xMidYMid slice"/></g>'
                    hs = hs.replace('<g class="up"', img_tag + '<g class="up"', 1)
                    open(hp, "w", encoding="utf-8").write(hs)
    print("Injected daily-pic into stack SVGs & ensured avatar")
