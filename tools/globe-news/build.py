"""Build the Globe News concept page (assets/globe/news.html) from tools/globe-news/.
Edit page.html (layout, CSS and behaviour) or news-demo.json (stories), then run:  python3 tools/globe-news/build.py && python3 build.py
Land dots come from tools/globe/dots.json; country shapes from countries-110m.json (world-atlas 2.0.2, Natural Earth, public domain).
news-demo.json is DEMO content: the page loads it from assets/globe/news-demo.json, so a live pipeline only has to write that file."""
import json, os, shutil
G = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(os.path.dirname(G))

# TopoJSON -> [name, centroid lon*10, centroid lat*10, [ring as flat lon*10,lat*10,...], ...] per country
topo = json.load(open(os.path.join(G, 'countries-110m.json')))
sx, sy = topo['transform']['scale']; tx, ty = topo['transform']['translate']
arcs = []
for a in topo['arcs']:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
def ring(ix):
    out = []
    for i in ix:
        p = arcs[i] if i >= 0 else arcs[~i][::-1]
        out.extend(p if not out else p[1:])
    return out
def area_c(r):
    a = cx = cy = 0
    for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1]):
        f = x0 * y1 - x1 * y0; a += f; cx += (x0 + x1) * f; cy += (y0 + y1) * f
    return (abs(a) / 2, (cx / (3 * a), cy / (3 * a))) if a else (0, r[0])
C = []
for g in topo['objects']['countries']['geometries']:
    name = g['properties']['name']
    if name == 'Antarctica' or 'arcs' not in g: continue
    polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
    rings = [ring(r) for p in polys for r in p]
    big = max((area_c(ring(p[0])) for p in polys), key=lambda t: t[0])
    row = [name, round(big[1][0] * 10), round(big[1][1] * 10)]
    for r in rings:
        flat = []
        for lo, la in r: flat += [round(lo * 10), round(la * 10)]
        row.append(flat)
    C.append(row)

page = open(os.path.join(G, 'page.html'), encoding='utf-8').read()
page = page.replace('__DOTS__', open(os.path.join('/'.join([SITE, 'tools/globe']), 'dots.json')).read()).replace('__COUNTRIES__', json.dumps(C, separators=(',', ':')))
out = os.path.join(SITE, 'assets/globe/news.html')
open(out, 'w', encoding='utf-8').write(page)
shutil.copy(os.path.join(G, 'news-demo.json'), os.path.join(SITE, 'assets/globe/news-demo.json'))
print('built', out, len(page) // 1024, 'KB,', len(C), 'countries')
