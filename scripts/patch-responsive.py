"""Inject nsc-responsive.css and nsc-responsive.js on all public HTML pages."""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_FILE = ROOT / "nsc-responsive.css"
JS_FILE = ROOT / "nsc-responsive.js"

CSS_LINK = '<link rel="stylesheet" href="{href}"/>'
JS_SCRIPT = '<script src="{href}" defer></script>'

VIEWPORT_META = (
    '<meta content="width=device-width, initial-scale=1.0, viewport-fit=cover" '
    'name="viewport"/>'
)
VIEWPORT_RE = re.compile(
    r'<meta[^>]+name=["\']viewport["\'][^>]*/?>',
    re.IGNORECASE,
)


def rel_href(html_path: Path, asset: Path) -> str:
    return Path(os.path.relpath(asset, html_path.parent)).as_posix()


def ensure_viewport(text: str) -> str:
    if VIEWPORT_RE.search(text):
        return VIEWPORT_RE.sub(VIEWPORT_META, text, count=1)
    if "<head>" in text:
        return text.replace("<head>", "<head>\n" + VIEWPORT_META, 1)
    return text


def ensure_css_link(text: str, href: str) -> str:
    marker = f'href="{href}"'
    if marker in text:
        return text
    link = CSS_LINK.format(href=href)
    chrome = re.search(
        r'(<link[^>]+href=["\'][^"\']*site-chrome\.css["\'][^>]*/?>)',
        text,
    )
    if chrome:
        return text.replace(chrome.group(1), chrome.group(1) + "\n" + link, 1)
    reveal = re.search(
        r'(<link[^>]+href=["\'][^"\']*nsc-reveal\.css["\'][^>]*/?>)',
        text,
    )
    if reveal:
        return text.replace(reveal.group(1), reveal.group(1) + "\n" + link, 1)
    if "</head>" in text:
        return text.replace("</head>", link + "\n</head>", 1)
    return text


def ensure_js_script(text: str, href: str) -> str:
    marker = f'src="{href}"'
    if marker in text:
        return text
    script = JS_SCRIPT.format(href=href)
    skel = re.search(
        r'(<script[^>]+src=["\'][^"\']*nsc-skeleton\.js["\'][^>]*></script>)',
        text,
    )
    if skel:
        return text.replace(skel.group(1), skel.group(1) + "\n" + script, 1)
    secure = re.search(
        r'(<script[^>]+src=["\'][^"\']*nsc-secure-login\.js["\'][^>]*></script>)',
        text,
    )
    if secure:
        return text.replace(secure.group(1), script + "\n" + secure.group(1), 1)
    if "</body>" in text:
        return text.replace("</body>", script + "\n</body>", 1)
    return text


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    css_href = rel_href(path, CSS_FILE)
    js_href = rel_href(path, JS_FILE)
    text = ensure_viewport(text)
    text = ensure_css_link(text, css_href)
    text = ensure_js_script(text, js_href)
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed = 0
    for fp in sorted(ROOT.rglob("*.html")):
        if "node_modules" in fp.parts or ".firecrawl" in fp.parts or "graphify-out" in fp.parts:
            continue
        if fp.parent == ROOT / "scripts":
            continue
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"Patched {changed} HTML file(s) with nsc-responsive assets")


if __name__ == "__main__":
    main()
