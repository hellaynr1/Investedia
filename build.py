"""Build the static site: wraps each page in src/pages/ with the shared <head> and scripts.
Run:  python3 build.py   (outputs the .html files at the project root)"""
import json, pathlib, re, html
from tools import legal_check

ROOT = pathlib.Path(__file__).parent
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="assets/consent.css?v={ver}">
<script src="assets/consent.js?v={ver}"></script>
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
<link rel="stylesheet" href="assets/app.css?v={ver}">
<link rel="stylesheet" href="assets/skin.css?v={ver}">
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
<a class="skip-link" href="#main-content">Skip to main content</a>
<script src="assets/quotes.js"></script>
<script src="assets/news.js"></script>
<script src="assets/mock.js?v={ver}"></script>
<script src="assets/legal-owner.js?v={ver}"></script>
<link rel="stylesheet" href="assets/news-menu.css?v={ver}">
<script src="assets/live-config.js?v={ver}"></script>
<script src="assets/prefs.js?v={ver}"></script>
<script src="assets/peek.js?v={ver}"></script>
<script src="assets/sectors.js?v={ver}"></script>
<script src="assets/news-menu.js?v={ver}"></script>
<script src="assets/ui.js?v={ver}"></script>
<script src="assets/news-alerts.js?v={ver}" defer></script>
{extra}<main class="wrap" id="main-content" tabindex="-1">
"""
TAIL = "</main>\n</body>\n</html>\n"

def build(release=False):
    if release and legal_check.main():
        raise SystemExit(1)
    values = legal_check.config()
    pages = sorted(p for p in (ROOT / "src" / "pages").glob("*.html") if re.fullmatch(r"[a-z0-9-]+\.html", p.name))
    ver = code_version(pages)
    for p in pages:
        first, body = p.read_text().split("\n", 1)
        meta = json.loads(first)
        body = legal_check.render(body, values)
        mailbox_key = 'privacy_email' if p.stem in {'privacy','cookies'} else 'contact_email'
        if values.get(mailbox_key):
            mailbox = legal_check.html.escape(str(values[mailbox_key]), quote=True)
            body = body.replace('mailto:info@investedia.com', 'mailto:'+mailbox).replace('>info@investedia.com<','>'+mailbox+'<')
        if values.get('last_review_date'):
            date = legal_check.html.escape(str(values['last_review_date']), quote=True)
            body = re.sub(r'<time datetime="2026-10-22">22 October 2026</time>', '<time datetime="'+date+'">'+date+'</time>', body)
        extra = "".join(f'<script src="{s}?v={ver}"></script>\n' for s in meta.get("scripts", []))
        html = HEAD.format(title=meta["title"], desc=meta["desc"], key=meta["key"], extra=extra, ver=ver) + body.rstrip() + "\n" + TAIL
        if meta.get("redirect"):
            target = meta["redirect"]
            if not re.fullmatch(r"[a-z0-9-]+\.html", target) or target == p.name:
                raise ValueError(f"Invalid redirect: {p.name} -> {target}")
            html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width,initial-scale=1">'
                    '<meta name="robots" content="noindex"><title>Page moved — Investedia</title>'
                    f'<link rel="canonical" href="https://investedia.com/{target}">'
                    f'<meta http-equiv="refresh" content="0;url={target}"></head><body><main>'
                    f'<p>This page has moved. <a href="{target}">Continue to {"Home" if target == "index.html" else "Markets"}</a>.</p>'
                    f'<script>location.replace({json.dumps(target)})</script></main></body></html>')
        (ROOT / p.name).write_text(html)
    (ROOT / 'assets/legal-owner.js').write_text('window.InvLegal=' + json.dumps(values).replace('<', '\\u003c') + ';\n')
    security = legal_check.render((ROOT/'src/security.txt').read_text(), values, styled=False)
    if values.get('security_email'): security = security.replace('mailto:info@investedia.com', 'mailto:'+str(values['security_email']))
    (ROOT / '.well-known/security.txt').write_text(security)
    write_sw(pages)
    print(f"Built {len(pages)} pages: " + ", ".join(p.name for p in pages))
    mirror_docs()

def code_version(pages):
    """Short hash of the site's code and pages (not the price/news data), used to bust phone caches."""
    import hashlib
    h = hashlib.sha1()
    data = {"quotes.js", "news.js", "intraday.json", "data.js"}
    for f in sorted([f for f in (ROOT / "assets").glob("*.*") if f.name not in data and " " not in f.name and f.name != "legal-owner.js"] + list(pages) + [ROOT / "src" / "sw.js", ROOT/"legal-config.json", ROOT/"tools/legal-fields.json", ROOT/"build.py"]):
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
    docs.mkdir(exist_ok=True)
    pages = [p for p in (ROOT/'src/pages').glob('*.html') if re.fullmatch(r'[a-z0-9-]+\.html',p.name)]
    for f in [ROOT/p.name for p in pages] + [ROOT / n for n in ("CNAME", ".nojekyll", "sitemap.xml", "robots.txt", "manifest.webmanifest", "sw.js")]:
        if f.exists(): shutil.copy2(f, docs / f.name)
    def ignore_copies(directory, names):
        return [name for name in names if re.search(r' \d+(?:\.|$)',name)]
    shutil.copytree(ROOT / "assets", docs / "assets", dirs_exist_ok=True, ignore=ignore_copies)
    shutil.copytree(ROOT / "data", docs / "data", dirs_exist_ok=True, ignore=ignore_copies)
    shutil.copytree(ROOT / ".well-known", docs / ".well-known", dirs_exist_ok=True, ignore=ignore_copies)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true", help="Fail if owner facts remain unresolved")
    build(release=parser.parse_args().release)
