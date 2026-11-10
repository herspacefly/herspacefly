"""Check the actual public deliverables, local links, and image security boundary."""
from pathlib import Path
import base64
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ns = '{http://www.w3.org/2000/svg}'
files = sorted((ROOT / 'assets').glob('*.svg'))
embedded_sources = {}
for path in sorted((ROOT/'assets/display').iterdir()):
    if path.suffix not in {'.png', '.webp'}:
        continue
    mime = 'image/png' if path.suffix == '.png' else 'image/webp'
    data = path.read_bytes()
    embedded_sources[f'data:{mime};base64,'+base64.b64encode(data).decode('ascii')] = path.name
assert len(embedded_sources) == 11, 'Expected ten art prints and one seal display copy'
assert len(files) == 14, f'Expected 14 plates, found {len(files)}'
for file in files:
    raw = file.read_text(encoding='utf-8')
    root = ET.fromstring(raw)
    assert root.tag == ns + 'svg', file
    assert root.find(ns + 'title') is not None, file
    assert root.find(ns + 'desc') is not None, file
    assert int(root.get('width')) > 0 and int(root.get('height')) > 0, file
    limit = 2_500_000 if file.name.startswith(('cover-', 'interlude-')) else 800_000
    assert file.stat().st_size < limit, f'Oversized artwork: {file}'
    for el in root.iter():
        assert el.tag not in {ns+'script',ns+'foreignObject'}, file
        assert not any(k.lower().startswith('on') for k in el.attrib), file
        for key, value in el.attrib.items():
            if 'href' in key:
                assert el.tag == ns+'image' and value in embedded_sources, file
        if el.tag == ns+'image':
            assert el.get('href') in embedded_sources, file
            x,y,iw,ih = (float(el.get(k)) for k in ['x','y','width','height'])
            assert x >= 0 and y >= 0 and x+iw <= float(root.get('width')) and y+ih <= float(root.get('height')), file
    assert 'prefers-reduced-motion' in raw, file
readme=(ROOT/'README.md').read_text(encoding='utf-8')
links=re.findall(r'(?:src|srcset)="([^"]+)"',readme)
for link in links:
    assert not link.startswith(('http:', 'https:')), f'Unexpected remote asset: {link}'
    assert (ROOT/link.split('?', 1)[0]).is_file(), f'Missing README image: {link}'
assert len(links) == 14, f'Unexpected image reference count: {len(links)}'
source = ET.parse(ROOT/'assets/source/portal-art.svg').getroot()
source_paths = [el.get('d') for el in source.iter(ns+'path')]
for file in (ROOT/'assets').glob('cover-*.svg'):
    root = ET.parse(file).getroot()
    portrait = next(el for el in root.iter(ns+'g') if el.get('id') == 'portal-Frame-285')
    assert [el.get('d') for el in portrait.iter(ns+'path')] == source_paths, file
    assert len(list(root.iter(ns+'image'))) == 1, file
for file in (ROOT/'assets').glob('interlude-*.svg'):
    root = ET.parse(file).getroot()
    assert len(list(root.iter(ns+'image'))) == 10, file
assert readme.count('<details>') == readme.count('</details>') == 1
print(f'PASS: {len(files)} valid local SVGs, {len(links)} resolving README images, 11 approved embedded display images, responsive themes, accessible descriptions, no scripts or external resources.')
