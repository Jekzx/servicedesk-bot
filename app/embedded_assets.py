"""Embedded and cached frontend assets for local and serverless execution."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

_cached_html = None
_cached_css = None
_cached_js = None


def get_html_content() -> str:
    global _cached_html
    if _cached_html:
        return _cached_html
    candidates = [
        BASE_DIR / "templates" / "index.html",
        Path.cwd() / "templates" / "index.html",
        Path("/var/task") / "templates" / "index.html",
        Path(__file__).resolve().parent / "templates" / "index.html",
    ]
    for p in candidates:
        if p.exists():
            _cached_html = p.read_text(encoding="utf-8")
            return _cached_html
    return "<h1>Service Desk Bot API is running! Access <a href='/docs'>/docs</a> for Swagger UI.</h1>"


def get_css_content() -> str:
    global _cached_css
    if _cached_css:
        return _cached_css
    candidates = [
        BASE_DIR / "static" / "style.css",
        Path.cwd() / "static" / "style.css",
        Path("/var/task") / "static" / "style.css",
        Path(__file__).resolve().parent / "static" / "style.css",
    ]
    for p in candidates:
        if p.exists():
            _cached_css = p.read_text(encoding="utf-8")
            return _cached_css
    return "/* CSS */"


def get_js_content() -> str:
    global _cached_js
    if _cached_js:
        return _cached_js
    candidates = [
        BASE_DIR / "static" / "app.js",
        Path.cwd() / "static" / "app.js",
        Path("/var/task") / "static" / "app.js",
        Path(__file__).resolve().parent / "static" / "app.js",
    ]
    for p in candidates:
        if p.exists():
            _cached_js = p.read_text(encoding="utf-8")
            return _cached_js
    return "// JS"
