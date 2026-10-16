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
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="assets/app.css">
</head>
<body data-page="{key}">
<script src="assets/mock.js"></script>
<script src="assets/ui.js"></script>
{extra}<main class="wrap">
"""
TAIL = "</main>\n</body>\n</html>\n"

def build():
    pages = sorted((ROOT / "src" / "pages").glob("*.html"))
    for p in pages:
        first, body = p.read_text().split("\n", 1)
        meta = json.loads(first)
        extra = "".join(f'<script src="{s}"></script>\n' for s in meta.get("scripts", []))
        html = HEAD.format(title=meta["title"], desc=meta["desc"], key=meta["key"], extra=extra) + body.rstrip() + "\n" + TAIL
        (ROOT / p.name).write_text(html)
    print(f"Built {len(pages)} pages: " + ", ".join(p.name for p in pages))

if __name__ == "__main__":
    build()
