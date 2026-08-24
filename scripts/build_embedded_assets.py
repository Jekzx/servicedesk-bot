"""Build script to embed frontend assets into Python module and templates."""
import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
raw_html = (base_dir / "templates" / "index.html").read_text(encoding="utf-8")
css_content = (base_dir / "static" / "style.css").read_text(encoding="utf-8")
js_content = (base_dir / "static" / "app.js").read_text(encoding="utf-8")

# Produce inlined HTML
inlined_html = raw_html
if '<link rel="stylesheet" href="/static/style.css">' in inlined_html:
    inlined_html = inlined_html.replace(
        '<link rel="stylesheet" href="/static/style.css">',
        f'<style>\n{css_content}\n</style>'
    )

if '<script src="/static/app.js"></script>' in inlined_html:
    inlined_html = inlined_html.replace(
        '<script src="/static/app.js"></script>',
        f'<script>\n{js_content}\n</script>'
    )

# Overwrite templates/index.html with the fully inlined version
(base_dir / "templates" / "index.html").write_text(inlined_html, encoding="utf-8")

# Generate app/embedded_assets.py
header = '"""Embedded frontend assets for guaranteed 100% availability in serverless environments."""\n'
header += 'from pathlib import Path\n\n'
header += 'BASE_DIR = Path(__file__).resolve().parent.parent\n\n'
header += f'EMBEDDED_HTML = {json.dumps(inlined_html)}\n'
header += f'EMBEDDED_CSS = {json.dumps(css_content)}\n'
header += f'EMBEDDED_JS = {json.dumps(js_content)}\n\n'

functions = """
def get_html_content() -> str:
    candidates = [
        BASE_DIR / "templates" / "index.html",
        Path.cwd() / "templates" / "index.html",
        Path("/var/task") / "templates" / "index.html",
    ]
    for p in candidates:
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                pass
    return EMBEDDED_HTML


def get_css_content() -> str:
    candidates = [
        BASE_DIR / "static" / "style.css",
        Path.cwd() / "static" / "style.css",
        Path("/var/task") / "static" / "style.css",
    ]
    for p in candidates:
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                pass
    return EMBEDDED_CSS


def get_js_content() -> str:
    candidates = [
        BASE_DIR / "static" / "app.js",
        Path.cwd() / "static" / "app.js",
        Path("/var/task") / "static" / "app.js",
    ]
    for p in candidates:
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                pass
    return EMBEDDED_JS
"""

(base_dir / "app" / "embedded_assets.py").write_text(header + functions, encoding="utf-8")
print("Templates and embedded assets updated successfully!")
