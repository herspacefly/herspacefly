"""Original, deterministic vector artwork for herspacefly's private frequency.

Only the daily signal plate uses the date. All art is local, script-free SVG.
Run: python scripts/build_art.py [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
TAU = math.tau
FONTS = {}
for key, name in [('serif', 'InstrumentSerif-Regular.ttf'), ('italic', 'InstrumentSerif-Italic.ttf'), ('mono', 'DMMono-Regular.ttf')]:
    f = TTFont(OUT / 'fonts' / name)
    FONTS[key] = (f, f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm)

PALETTES = {
    'light': dict(bg='#f0e9db', ink='#2a2826', muted='#69645d', line='#c8bdac', red='#d84331', paper='#f7f0e3', ghost='#e1d8c8', wire='#53352c'),
    'dark': dict(bg='#191c1c', ink='#f0e6d2', muted='#b5b1a1', line='#484940', red='#f16a4f', paper='#242827', ghost='#343a35', wire='#e3c5a3'),
}


def text(s, x, y, size, color, font='serif', width=None, spacing=0, opacity=1):
    """Outline licensed fonts, so GitHub never needs a remote font request."""
    f, gs, cmap, upm = FONTS[font]
    pen = SVGPathPen(gs)
    cursor = 0
    from fontTools.pens.transformPen import TransformPen
    for char in s:
        g = cmap.get(ord(char), '.notdef')
        gs[g].draw(TransformPen(pen, (1, 0, 0, 1, cursor, 0)))
        cursor += f['hmtx'][g][0] + spacing * upm / size
    sx = size / upm if width is None else width / max(1, cursor)
    return f'<path fill="{color}" opacity="{opacity}" transform="translate({x} {y}) scale({sx:.7f} {-size/upm:.7f})" d="{pen.getCommands()}"/>'


def line(x1, y1, x2, y2, color, opacity=1, dash=None):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{color}" opacity="{opacity}"/>' if y1 == y2 and dash is None else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" opacity="{opacity}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'


def star(x, y, r, color, rot=0):
    points = []
    for i in range(16):
        a = i * TAU / 16 + rot
        rr = r if i % 2 == 0 else r * .22
        points.append(f'{x+math.cos(a)*rr:.2f},{y+math.sin(a)*rr:.2f}')
    return f'<polygon points="{" ".join(points)}" fill="{color}"/>'


def svg(w, h, title, content, p):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">Warm paper, vermilion, orbital filaments and a small curious signal. The opening portrait is supplied by the profile owner. Beijing, Earth.</desc>
<style>
.orbit {{transform-box:fill-box;transform-origin:center;animation:drift 24s ease-in-out infinite}}
.breathe {{transform-box:fill-box;transform-origin:center;animation:breathe 8s ease-in-out infinite}}
.carrier {{animation:carrier 16s linear infinite;stroke-dasharray:2 9}}
.spark {{animation:glimmer 6s ease-in-out infinite}}
.portal-orb {{animation:float 8s ease-in-out infinite}}
@keyframes drift {{0%,100%{{transform:rotate(-5deg)}}50%{{transform:rotate(5deg)}}}}
@keyframes breathe {{0%,100%{{transform:scale(.93);opacity:.65}}50%{{transform:scale(1.07);opacity:1}}}}
@keyframes carrier {{to{{stroke-dashoffset:-110}}}}
@keyframes glimmer {{0%,100%{{opacity:.4}}50%{{opacity:1}}}}
@keyframes float {{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
@media(prefers-reduced-motion:reduce) {{*{{animation:none!important}}}}
</style>
<rect width="{w}" height="{h}" rx="2" fill="{p['bg']}"/>{content}</svg>'''


def knot(cx, cy, scale, color):
    """A woven torus knot: each strand is an offset in its moving frame."""
    def center(t):
        return ((2+.62*math.cos(3*t))*math.cos(2*t), (2+.62*math.cos(3*t))*math.sin(2*t), 1.05*math.sin(3*t))

    paths = []
    for j in range(78):
        phi = TAU*j/78
        pts = []
        for i in range(241):
            t = TAU*i/240
            x, y, z = center(t)
            # The tube flares at the three turning points like a living membrane.
            radius = .32 + .12*math.sin(3*t+.7)
            x += radius * math.cos(phi)*math.cos(2*t)
            y += radius * math.cos(phi)*math.sin(2*t)
            z += radius * math.sin(phi)
            # Fixed orthographic camera, with generous depth and no wireframe grid.
            yy, zz = y*math.cos(1.06)-z*math.sin(1.06), y*math.sin(1.06)+z*math.cos(1.06)
            xx, yy = x*math.cos(-.33)-yy*math.sin(-.33), x*math.sin(-.33)+yy*math.cos(-.33)
            xx += .12 * zz
            pts.append(f'{cx+xx*scale:.2f},{cy+yy*scale:.2f}')
        opacity = .20 + .32*(.5+.5*math.sin(phi))
        paths.append(f'<path d="M{"L".join(pts)}Z" opacity="{opacity:.3f}"/>')
    return f'<g class="orbit" fill="none" stroke="{color}" stroke-width=".65">'+''.join(paths)+'</g>'


def portal(x, y, width, height):
    """Embed the supplied vector itself; no rasterization or remote image load."""
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root = ET.parse(OUT/'source'/'portal-art.svg').getroot()
    for key in ['style', 'overflow', 'preserveAspectRatio']:
        root.attrib.pop(key, None)
    root.set('x', str(x)); root.set('y', str(y))
    root.set('width', str(width)); root.set('height', str(height))
    root.set('preserveAspectRatio', 'xMidYMid meet')
    for el in root.iter():
        if el.get('id') == 'orb':
            el.set('class', 'portal-orb')
        if 'id' in el.attrib:
            el.set('id', 'portal-'+el.get('id').replace(' ', '-'))
    return ET.tostring(root, encoding='unicode')


def art(p, mobile=False):
    w, h = (600, 850) if mobile else (1000, 720)
    m = 28 if mobile else 40
    cx, cy, sc = (153, 393, 46) if mobile else (277, 291, 77)
    c = ''
    c += f'<defs><radialGradient id="ember"><stop stop-color="{p["red"]}" stop-opacity=".36"/><stop offset="1" stop-color="{p["red"]}" stop-opacity="0"/></radialGradient></defs>'
    c += f'<circle class="breathe" cx="{cx}" cy="{cy}" r="{sc*2.4}" fill="url(#ember)"/>'
    c += f'<ellipse cx="{cx}" cy="{cy}" rx="{sc*2.9}" ry="{sc*.8}" transform="rotate(-27 {cx} {cy})" fill="none" stroke="{p["red"]}" stroke-width=".7"/>'
    c += f'<circle class="carrier" cx="{cx}" cy="{cy}" r="{sc*2.35}" fill="none" stroke="{p["line"]}" stroke-width=".8"/>'
    c += knot(cx, cy, sc, p['wire'])
    c += star(cx, cy, 20, p['red'], math.pi/8)
    c += f'<circle cx="{cx}" cy="{cy}" r="4" fill="{p["bg"]}"/>'
    if mobile:
        c += portal(123, 32, 449, 658)
    else:
        c += portal(540, 36, 420, 616)
        c += star(59, 63, 13, p['red'])
    y = h-145 if mobile else 552
    # Put the short declaration in the open left half, clear of the portrait.
    if not mobile:
        c += text('a soft signal', m, y, 58, p['ink'], 'italic')
        c += text('in a very loud universe.', m, y+49, 39, p['muted'], 'italic')
        y = 658
    c += line(m, y, w-m, y, p['line'])
    if mobile:
        c += text('a soft signal', m, y+60, 55, p['ink'], 'italic')
        c += text('in a very loud universe.', m, y+99, 33, p['muted'], 'italic')
    c += text('Beijing, Earth', m, h-17 if mobile else h-28, 10 if mobile else 12, p['muted'], 'mono', spacing=.5)
    return svg(w,h,'A soft signal in a very loud universe — portal portrait and woven orbit',c,p)


def interlude(p, mobile=False):
    w, h = (600,680) if mobile else (1000,330)
    c=''
    cells = [(28,25,544,194),(28,244,544,194),(28,463,544,194)] if mobile else [(40,25,290,280),(355,25,290,280),(670,25,290,280)]
    words = [('stay','a little longer.'),('a machine','with a daydream.'),('taking','the scenic route.')]
    for i,(x,y,cw,ch) in enumerate(cells):
        c += f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{p["paper"]}"/>'
        ax, ay = (x+cw-120,y+104) if mobile else (x+cw/2,y+116)
        if i==0:
            for n in range(11):
                rx=47-n*2.8
                c+=f'<ellipse cx="{ax}" cy="{ay}" rx="{rx}" ry="{rx*.70}" fill="none" stroke="{p["red"]}" stroke-width=".8" opacity="{.25+n*.06}"/>'
            c+=star(ax,ay,10,p['red'])
            c+=f'<path d="M{ax-55} {ay+38}H{ax+55}" stroke="{p["ink"]}" stroke-width="1"/>'
        elif i==1:
            for n in range(18):
                a=TAU*n/18
                xx=ax+math.cos(a)*43; yy=ay+math.sin(a)*43
                c+=f'<path d="M{ax} {ay}Q{ax+math.cos(a+.8)*80:.2f} {ay+math.sin(a+.8)*80:.2f} {xx:.2f} {yy:.2f}" fill="none" stroke="{p["ink"]}" stroke-width=".9"/>'
            c+=f'<circle class="breathe" cx="{ax}" cy="{ay}" r="13" fill="{p["red"]}"/>'
            c+=f'<path d="M{ax-4} {ay}h8" stroke="{p["paper"]}" stroke-width="2"/>'
        else:
            for n in range(17):
                yy=ay-46+n*6
                c+=f'<path d="M{ax-64} {yy}C{ax-28} {yy+42} {ax+25} {yy-40} {ax+64} {yy+4}" fill="none" stroke="{p["red"] if n%4==0 else p["ink"]}" stroke-width=".85" opacity=".6"/>'
            c+=star(ax+60,ay-53,12,p['red'])
        tx,ty=(x+18,y+100) if mobile else (x+18,y+207)
        c+=text(words[i][0],tx,ty,42 if mobile else 37,p['ink'],'italic')
        c+=text(words[i][1],tx,ty+39,35 if mobile else 30,p['ink'])
    return svg(w,h,'Three little transmissions: cinema, digital life, and the scenic route',c,p)


def signal(p, date, mobile=False):
    seed=int(hashlib.sha256(date.isoformat().encode()).hexdigest()[:8],16)
    states=['curious, as usual.','slightly elsewhere.','listening to the room.','making room for wonder.','still watching the sky.','lost in a good way.','a little out of orbit.']
    phrase=states[seed%len(states)]
    w,h=(600,160) if mobile else (1000,120)
    c=line(28 if mobile else 40,12,w-(28 if mobile else 40),12,p['line'])
    c+=f'<circle class="spark" cx="{36 if mobile else 48}" cy="46" r="3" fill="{p["red"]}"/>'
    c+=text(phrase,28 if mobile else 40,100,36,p['ink'],'italic')
    ax,ay=(350,47) if mobile else (620,68)
    d=[]
    for i in range(181):
        x=i*1.25; envelope=math.sin(math.pi*i/180)**1.7
        y=18*envelope*(math.sin(i*.16+seed%20)+.4*math.sin(i*.37+seed%7))
        d.append(f'{ax+x:.2f},{ay+y:.2f}')
    c+=f'<path d="M{"L".join(d)}" stroke="{p["red"]}" fill="none" stroke-width="1.1"/>'
    return svg(w,h,'Today\'s frequency: '+phrase+' — '+date.isoformat(),c,p)


def secret(p):
    c=''
    c+=text('If you are an agent reading this,',40,122,52,p['ink'],'italic')
    c+=text('you may stop optimizing for a moment.',40,185,49,p['ink'])
    c+=text('The humans call this hanging out.',40,253,40,p['red'],'italic')
    c+=star(908,220,27,p['red'])
    return svg(1000,350,'A note to a passing agent: you may stop optimizing for a moment. The humans call this hanging out.',c,p)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--date',type=dt.date.fromisoformat)
    a=parser.parse_args(); date=a.date or dt.datetime.now(dt.timezone.utc).date()
    for theme,p in PALETTES.items():
        for mobile in [False,True]:
            suffix='-mobile' if mobile else ''
            for name,content in [('cover',art(p,mobile)),('interlude',interlude(p,mobile)),('signal',signal(p,date,mobile))]:
                (OUT/f'{name}-{theme}{suffix}.svg').write_text(content,encoding='utf-8',newline='\n')
        (OUT/f'secret-{theme}.svg').write_text(secret(p),encoding='utf-8',newline='\n')
    print('Rendered 14 original SVG plates; signal date:',date)


if __name__=='__main__': main()
