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
.orbit {{transform-box:view-box;animation:revolve 18s linear infinite}}
.breathe {{transform-box:fill-box;transform-origin:center;animation:breathe 8s ease-in-out infinite}}
.carrier {{animation:carrier 16s linear infinite;stroke-dasharray:2 9}}
.portal-orb {{animation:float 8s ease-in-out infinite}}
@keyframes revolve {{from{{transform:rotate(-12deg)}}to{{transform:rotate(348deg)}}}}
@keyframes breathe {{0%,100%{{transform:scale(.93);opacity:.65}}50%{{transform:scale(1.07);opacity:1}}}}
@keyframes carrier {{to{{stroke-dashoffset:-110}}}}
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
    encoded = base64.b64encode((OUT/'source'/name).read_bytes()).decode('ascii')
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
    w, h = (600, 850) if mobile else (1000, 720)
    m = 28 if mobile else 40
    cx, cy, sc = (153, 393, 46) if mobile else (275, 274, 73)
    c = ''
    c += f'<defs><radialGradient id="ember"><stop stop-color="{p["red"]}" stop-opacity=".24"/><stop offset="1" stop-color="{p["red"]}" stop-opacity="0"/></radialGradient></defs>'
    c += f'<circle class="breathe" cx="{cx}" cy="{cy}" r="{sc*2.4}" fill="url(#ember)"/>'
    c += f'<ellipse cx="{cx}" cy="{cy}" rx="{sc*2.9}" ry="{sc*.8}" transform="rotate(-27 {cx} {cy})" fill="none" stroke="{p["red"]}" stroke-width=".7"/>'
    c += f'<circle class="carrier" cx="{cx}" cy="{cy}" r="{sc*2.35}" fill="none" stroke="{p["line"]}" stroke-width=".8"/>'
    c += knot(cx, cy, sc, p['wire'])
    c += f'<circle cx="{cx}" cy="{cy}" r="3" fill="{p["red"]}"/>'
    if mobile:
        c += portal(123, 32, 449, 658)
    else:
        c += portal(540, 36, 420, 616)
    c += raster('signal-seal.png', 28 if mobile else 40, 28, 48 if mobile else 62, 48 if mobile else 62)
    c += wing(542 if mobile else 926, 755 if mobile else 666, 24 if mobile else 20, 58 if mobile else 40)
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
    w, h = (600, 1110) if mobile else (1000, 740)
    # Three complete images, with deliberately different scales and staggered edges.
    # Each is a self-contained data URI, not an external load from inside SVG.
    prints = [
        ('mission-header.webp', 28, 28, 484, 484),
        ('hero.webp', 222, 544, 350, 377),
        ('footer-field.webp', 28, 866, 330, 214),
    ] if mobile else [
        ('mission-header.webp', 40, 28, 500, 500),
        ('hero.webp', 594, 104, 330, 356),
        ('footer-field.webp', 398, 480, 360, 234),
    ]
    c = ''
    for name, x, y, pw, ph in prints:
        c += f'<rect x="{x-6+4}" y="{y-6+5}" width="{pw+12}" height="{ph+12}" fill="{p["ink"]}" opacity=".10"/>'
        c += f'<rect x="{x-6}" y="{y-6}" width="{pw+12}" height="{ph+12}" fill="{p["paper"]}"/>'
        c += raster(name, x, y, pw, ph)
    return svg(w,h,'A little cabinet of digital dreams: a gaze, a winged figure, and a floating light',c,p)


def signal(p, date, mobile=False):
    seed=int(hashlib.sha256(date.isoformat().encode()).hexdigest()[:8],16)
    states=['curious, as usual.','slightly elsewhere.','listening to the room.','making room for wonder.','still watching the sky.','lost in a good way.','a little out of orbit.']
    phrase=states[seed%len(states)]
    w,h=(600,105) if mobile else (1000,105)
    c=text(phrase,28 if mobile else 40,70,36,p['ink'],'italic')
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
