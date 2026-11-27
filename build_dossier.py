import base64, io, html, os
from PIL import Image

MONO="ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"
SANS="-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
RED="#ff3b30"
BG="#0b0b0c"; PANEL="#131315"; LINE="#2a2a2e"; TXT="#f2f2f2"; DIM="#85858c"

# avatar -> small embedded data uri
im=Image.open('/home/heck43/.gemini/antigravity/brain/e37e2ebb-3b2f-475a-a5ff-ed5e3e0bf2d8/scratch/img/top-avatar.png').convert('RGBA').resize((200,200))
buf=io.BytesIO(); im.save(buf,'PNG',optimize=True)
AV="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()

def dots(x,y,cols,rows,gap=8,r=1.4,fill="#3a3a3f"):
    return ''.join(f'<circle cx="{x+i*gap}" cy="{y+j*gap}" r="{r}" fill="{fill}"/>' for i in range(cols) for j in range(rows))

def field(x,y,label,value,w=190):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{DIM}">{label}</text>'
            f'<text x="{x}" y="{y+22}" font-family="{SANS}" font-size="16" font-weight="600" fill="{TXT}">{html.escape(value)}</text>')

def hero():
    W,H=900,356
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="24" fill="{BG}" stroke="{LINE}"/>',
       dots(560,26,40,3,gap=8.5),
       # photo block
       f'<clipPath id="a"><rect x="32" y="64" width="190" height="190" rx="22"/></clipPath>',
       f'<image href="{AV}" x="32" y="64" width="190" height="190" clip-path="url(#a)" preserveAspectRatio="xMidYMid slice"/>',
       f'<rect x="32.5" y="64.5" width="189" height="189" rx="22" fill="none" stroke="{LINE}"/>',
       # corner ticks
       *[f'<path d="{d}" stroke="{RED}" stroke-width="2" fill="none" stroke-linecap="round"/>' for d in
         ["M24 90V72a8 8 0 0 1 8-8h18","M230 90V72a8 8 0 0 0-8-8h-18","M24 228v18a8 8 0 0 0 8 8h18","M230 228v18a8 8 0 0 1-8 8h-18"]],
       # status
       f'<circle cx="40" cy="36" r="4" fill="{RED}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>',
       f'<text x="52" y="40" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{DIM}">ONLINE · PROFILE / 126146783</text>',
       # name
       f'<text x="262" y="112" font-family="{SANS}" font-size="66" font-weight="800" letter-spacing="-2" fill="{TXT}">heck43<tspan fill="{RED}">.</tspan></text>',
       f'<text x="264" y="142" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{DIM}">DEV · STUDENT · FURRY · TINKERER</text>',
       f'<line x1="262" y1="164" x2="868" y2="164" stroke="{LINE}"/>',
       field(262,196,"AGE","18"),
       field(402,196,"BASE","Кострома"),
       field(572,196,"STUDY","Top Academy · 3 курс"),
       field(262,254,"MAKES","моды Telegram, игры, MCP"),
       field(572,254,"PLAYS","Minecraft · Postal 2 · ATLYSS"),
       f'<line x1="32" y1="302" x2="868" y2="302" stroke="{LINE}"/>',
       f'<text x="32" y="330" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{DIM}">STACK</text>',
    ]
    x=100
    for s in ["PYTHON","C#","C++","JAVASCRIPT","JAVA","LUAU"]:
        w=len(s)*8+22
        o.append(f'<rect x="{x}" y="316" width="{w}" height="22" rx="11" fill="none" stroke="{LINE}"/><text x="{x+w/2}" y="331" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="1" fill="{TXT}">{s}</text>')
        x+=w+8
    o.append('</svg>')
    open('assets/hero.svg','w').write(''.join(o))

PROJ=[("pawgram","Telegram Desktop с модами","C++"),("Pawgram-Android","Telegram-клиент под Android","Java"),
("furry-quest","Экшен-рогалик","JavaScript"),("mcp-arma3","MCP-сервер: ИИ ↔ Arma 3","MCP"),
("plushlair-mobile","Мобильное приложение магазина","JavaScript"),("Chess-isometry-Rework","Изометрические шахматы","Python")]
def rows():
    for i,(n,d,l) in enumerate(PROJ):
        W,H=900,64
        s=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="{PANEL}" stroke="{LINE}"/>
<rect x=".5" y=".5" width="0" height="{H-1}" rx="16" fill="{RED}" fill-opacity=".12"><animate attributeName="width" from="0" to="0"/></rect>
<text x="28" y="39" font-family="{MONO}" font-size="13" fill="{RED}">{i+1:02d}</text>
<text x="70" y="39" font-family="{SANS}" font-size="18" font-weight="700" fill="{TXT}">{html.escape(n)}</text>
<text x="330" y="38" font-family="{SANS}" font-size="14" fill="{DIM}">{html.escape(d)}</text>
<text x="780" y="38" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{TXT}">{l.upper()}</text>
<circle cx="845" cy="32" r="14" fill="none" stroke="{LINE}"/>
<path d="M839 38 L851 26 M843 26 H851 V34" stroke="{TXT}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''
        open(f'assets/row{i}.svg','w').write(s)

os.makedirs('assets',exist_ok=True)
for f in os.listdir('assets'):
    p=os.path.join('assets',f)
    if os.path.isdir(p):
        for g in os.listdir(p): os.remove(os.path.join(p,g))
        os.rmdir(p)
hero(); rows()
links=''.join(f'<a href="https://github.com/Heck43/{n}"><img src="assets/row{i}.svg" width="100%" alt="{n}"/></a>\n<br/>\n' for i,(n,_,_) in enumerate(PROJ))
md=f'''<div align="center">

<img src="assets/hero.svg" width="100%" alt="heck43" />

<a href="https://heck43.github.io"><img src="https://img.shields.io/badge/SITE-heck43.github.io-0b0b0c?style=flat-square&labelColor=ff3b30" /></a>
<a href="https://t.me/Heck1337"><img src="https://img.shields.io/badge/TELEGRAM-@Heck1337-0b0b0c?style=flat-square&labelColor=ff3b30" /></a>
<a href="https://discord.gg/BMTCDDbpFh"><img src="https://img.shields.io/badge/DISCORD-join-0b0b0c?style=flat-square&labelColor=ff3b30" /></a>
<a href="mailto:lolnektyr@gmail.com"><img src="https://img.shields.io/badge/MAIL-lolnektyr@gmail.com-0b0b0c?style=flat-square&labelColor=ff3b30" /></a>

<br/><br/>

{links}
<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Heck43/Heck43/output/github-contribution-grid-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Heck43/Heck43/output/github-contribution-grid-snake.svg" />
  <img alt="contributions" src="https://raw.githubusercontent.com/Heck43/Heck43/output/github-contribution-grid-snake-dark.svg" width="100%" />
</picture>

</div>
'''
open('README.md','w').write(md)
