"""Build the static site: wraps each page in src/pages/ with the shared <head> and scripts.
Run:  python3 build.py   (outputs the .html files at the project root)"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta name="theme-color" content="#0A0A0B">
<meta property="og:type" content="website">
<meta property="og:image" content="assets/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="assets/app.css?v={ver}">
<link rel="apple-touch-icon" href="assets/app/apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Investedia">
<link rel="apple-touch-startup-image" media="screen and (device-width: 440px) and (device-height: 956px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="assets/app/splash-1320x2868.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 430px) and (device-height: 932px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="assets/app/splash-1290x2796.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 402px) and (device-height: 874px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="assets/app/splash-1206x2622.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="assets/app/splash-1179x2556.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 428px) and (device-height: 926px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="assets/app/splash-1284x2778.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 390px) and (device-height: 844px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="assets/app/splash-1170x2532.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="assets/app/splash-1125x2436.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="assets/app/splash-1242x2688.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 2) and (orientation: portrait)" href="assets/app/splash-828x1792.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2) and (orientation: portrait)" href="assets/app/splash-750x1334.png">
<link rel="apple-touch-startup-image" media="screen and (device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2) and (orientation: portrait)" href="assets/app/splash-640x1136.png">
</head>
<body data-page="{key}">
<script src="assets/quotes.js"></script>
<script src="assets/news.js"></script>
<script src="assets/home-data.js"></script>
<script src="assets/mock.js?v={ver}"></script>
<script src="assets/real-data.js?v={ver}"></script>
<script src="assets/ui.js?v={ver}"></script>
{extra}<main class="wrap">
"""
TAIL = '</main>\n<script src="assets/page-data.js"></script>\n</body>\n</html>\n'

def build():
    pages = sorted((ROOT / "src" / "pages").glob("*.html"))
    ver = code_version(pages)
    for p in pages:
        first, body = p.read_text().split("\n", 1)
        meta = json.loads(first)
        extra = "".join(f'<script src="{s}?v={ver}"></script>\n' for s in meta.get("scripts", []))
        html = HEAD.format(title=meta["title"], desc=meta["desc"], key=meta["key"], extra=extra, ver=ver) + body.rstrip() + "\n" + TAIL
        (ROOT / p.name).write_text(html)
    write_sw(pages)
    print(f"Built {len(pages)} pages: " + ", ".join(p.name for p in pages))
    mirror_docs()

def code_version(pages):
    """Short hash of the site's code and pages (not the price/news data), used to bust phone caches."""
    import hashlib
    h = hashlib.sha1()
    data = {"quotes.js", "news.js", "intraday.json", "data.js"}
    for f in sorted([f for f in (ROOT / "assets").glob("*.*") if f.name not in data] + list(pages) + [ROOT / "src" / "sw.js"]):
        h.update(f.read_bytes())
    return h.hexdigest()[:10]

def write_sw(pages):
    """Offline support for the home-screen app. The version changes whenever the site's code changes."""
    tpl = (ROOT / "src" / "sw.js").read_text()
    (ROOT / "sw.js").write_text(tpl.replace("__VERSION__", code_version(pages)))

def mirror_docs():
    """GitHub Pages may publish from /docs: keep an identical copy of the site there."""
    import shutil
    docs = ROOT / "docs"
    shutil.rmtree(docs, ignore_errors=True)
    docs.mkdir()
    for f in list(ROOT.glob("*.html")) + [ROOT / n for n in ("CNAME", ".nojekyll", "sitemap.xml", "robots.txt", "manifest.webmanifest", "sw.js")]:
        if f.exists():
            shutil.copy2(f, docs / f.name)
    shutil.copytree(ROOT / "assets", docs / "assets")

if __name__ == "__main__":
    build()
