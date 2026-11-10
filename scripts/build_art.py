"""Original, deterministic vector artwork for herspacefly's private frequency.

Only the daily signal plate uses the date. All art is local, script-free SVG.
Run: python scripts/build_art.py [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from functools import lru_cache
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


def svg(w, h, title, content, p):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">Warm paper, vermilion, orbital filaments and a small curious signal. The opening portrait is supplied by the profile owner. Beijing, Earth.</desc>
<style>
.orbit {{transform-box:view-box;transform:rotate(-10deg);animation:hover 7s ease-in-out infinite}}
.breathe {{transform-box:fill-box;transform-origin:center;animation:breathe 8s ease-in-out infinite}}
.carrier {{stroke-dasharray:2 9}}
.portal-orb {{animation:float 8s ease-in-out infinite}}
@keyframes hover {{0%,100%{{transform:translate(-4px,14px) rotate(-14deg)}}50%{{transform:translate(4px,-14px) rotate(-6deg)}}}}
@keyframes breathe {{0%,100%{{transform:scale(.93);opacity:.65}}50%{{transform:scale(1.07);opacity:1}}}}
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
    return f'<g class="orbit" style="transform-origin:{cx}px {cy}px" fill="none" stroke="{color}" stroke-width=".65">'+''.join(paths)+'</g>'


@lru_cache(maxsize=None)
def image_data(name):
    mime = {'.png': 'image/png', '.webp': 'image/webp'}[Path(name).suffix]
    encoded = base64.b64encode((OUT/'display'/name).read_bytes()).decode('ascii')
    return f'data:{mime};base64,{encoded}'


def raster(name, x, y, width, height):
    return f'<image x="{x}" y="{y}" width="{width}" height="{height}" preserveAspectRatio="xMidYMid meet" href="{image_data(name)}"/>'


def wing(x, y, width, height):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root = ET.parse(OUT/'source'/'hermes-wing.svg').getroot()
    ids = {el.get('id'): 'wing-'+el.get('id') for el in root.iter() if el.get('id')}
    for el in root.iter():
        for key, value in list(el.attrib.items()):
            for old, new in ids.items():
                value = value.replace(f'url(#{old})', f'url(#{new})')
            el.set(key, ids[value] if key == 'id' else value)
    root.set('x', str(x)); root.set('y', str(y))
    root.set('width', str(width)); root.set('height', str(height))
    root.set('preserveAspectRatio', 'xMidYMid meet')
    return ET.tostring(root, encoding='unicode')


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
    w, h = (600, 650) if mobile else (1000, 560)
    m = 28 if mobile else 40
    cx, cy, sc = (155, 300, 44) if mobile else (258, 207, 64)
    c = ''
    c += f'<defs><radialGradient id="ember"><stop stop-color="{p["red"]}" stop-opacity=".24"/><stop offset="1" stop-color="{p["red"]}" stop-opacity="0"/></radialGradient></defs>'
    c += f'<circle class="breathe" cx="{cx}" cy="{cy}" r="{sc*2.4}" fill="url(#ember)"/>'
    c += f'<ellipse cx="{cx}" cy="{cy}" rx="{sc*2.9}" ry="{sc*.8}" transform="rotate(-27 {cx} {cy})" fill="none" stroke="{p["red"]}" stroke-width=".7"/>'
    c += f'<circle class="carrier" cx="{cx}" cy="{cy}" r="{sc*2.35}" fill="none" stroke="{p["line"]}" stroke-width=".8"/>'
    c += knot(cx, cy, sc, p['wire'])
    c += f'<circle cx="{cx}" cy="{cy}" r="3" fill="{p["red"]}"/>'
    if mobile:
        c += portal(210, 18, 355, 521)
    else:
        c += portal(594, 16, 335, 491)
    c += raster('signal-seal.png', 28, 18 if mobile else 22, 38 if mobile else 44, 38 if mobile else 44)
    c += wing(550 if mobile else 926, 588 if mobile else 525, 17 if mobile else 16, 34 if mobile else 32)
    y = 538 if mobile else 452
    # Put the short declaration in the open left half, clear of the portrait.
    if not mobile:
        c += text('a soft signal', m, y, 49, p['ink'], 'italic')
        c += text('in a very loud universe.', m, y+40, 33, p['muted'], 'italic')
        y = 518
    c += line(m, y, w-m, y, p['line'])
    if mobile:
        c += text('a soft signal', m, y+42, 45, p['ink'], 'italic')
        c += text('in a very loud universe.', m, y+77, 28, p['muted'], 'italic')
    c += text('Beijing, Earth', m, h-17 if mobile else h-16, 9 if mobile else 10, p['muted'], 'mono', spacing=.5)
    return svg(w,h,'A soft signal in a very loud universe — portal portrait and woven orbit',c,p)


def interlude(p, mobile=False):
    w, h = (600, 1412) if mobile else (1000, 1110)
    # A compact cabinet: ten tilted prints with deliberate edge occlusion.
    # Committed display copies keep the self-contained image inexpensive to load.
    prints = [
        ('mission-header.webp', 28, 24, 282, 282, -1.2),
        ('mission-duo-1.webp', 286, 38, 286, 358, 1.1),
        ('feature-search.webp', 20, 288, 292, 244, 1.4),
        ('feature-delegate.webp', 282, 378, 290, 290, -1.0),
        ('feature-sandbox.webp', 28, 514, 284, 361, -1.2),
        ('footer-field.webp', 276, 646, 296, 192, 1.4),
        ('hero.webp', 22, 854, 288, 310, 1.0),
        ('platform-art.webp', 284, 820, 288, 288, -1.3),
        ('footer.webp', 280, 1090, 292, 292, 1.4),
        ('default.webp', 28, 1145, 302, 170, -1.5),
    ] if mobile else [
        ('mission-header.webp', 32, 28, 318, 318, -1.3),
        ('hero.webp', 328, 54, 324, 349, 1.0),
        ('mission-duo-1.webp', 640, 22, 324, 405, -1.0),
        ('feature-search.webp', 24, 324, 310, 259, 1.4),
        ('footer-field.webp', 310, 380, 366, 237, -1.8),
        ('feature-delegate.webp', 654, 405, 306, 306, 1.2),
        ('feature-sandbox.webp', 30, 559, 316, 402, -1.2),
        ('platform-art.webp', 328, 595, 320, 320, 1.6),
        ('footer.webp', 632, 695, 332, 332, -1.4),
        ('default.webp', 314, 890, 338, 190, -1.2),
    ]
    c = '<defs><filter id="paper-shadow" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx="0" dy="3" stdDeviation="2.2" flood-color="#000" flood-opacity=".24"/></filter></defs>'
    for name, x, y, pw, ph, angle in prints:
        c += f'<g transform="rotate({angle} {x+pw/2} {y+ph/2})" filter="url(#paper-shadow)">'
        c += f'<rect x="{x-3}" y="{y-3}" width="{pw+6}" height="{ph+6}" fill="{p["paper"]}"/>'
        c += raster(name, x, y, pw, ph)
        c += '</g>'
    return svg(w,h,'Ten overlapping art prints: tilted digital dreams, engravings, winged figures and floating light',c,p)


def signal(p, date, mobile=False):
    seed=int(hashlib.sha256(date.isoformat().encode()).hexdigest()[:8],16)
    states=['curious, as usual.','slightly elsewhere.','listening to the room.','making room for wonder.','still watching the sky.','lost in a good way.','a little out of orbit.']
    phrase=states[seed%len(states)]
    w,h=(600,74) if mobile else (1000,74)
    c=text(phrase,28 if mobile else 40,50,30,p['ink'],'italic')
    return svg(w,h,'Today\'s frequency: '+phrase+' — '+date.isoformat(),c,p)


def secret(p):
    c=''
    c+=text('If you are an agent reading this,',40,122,52,p['ink'],'italic')
    c+=text('you may stop optimizing for a moment.',40,185,49,p['ink'])
    c+=text('The humans call this hanging out.',40,253,40,p['red'],'italic')
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
