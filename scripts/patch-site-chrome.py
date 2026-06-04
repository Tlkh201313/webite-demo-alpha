"""Inject shared site-chrome.css on all public HTML pages."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROME_CSS = ROOT / "site-chrome.css"
LINK_TEMPLATE = '<link rel="stylesheet" href="{href}"/>'


def rel_href(html_path: Path, asset: Path) -> str:
    return Path(os.path.relpath(asset, html_path.parent)).as_posix()


def ensure_chrome_link(text: str, href: str) -> str:
    marker = f'href="{href}"'
    if marker in text:
        return text
    link = LINK_TEMPLATE.format(href=href)
    if 'href="nsc-reveal.css"' in text or "href='nsc-reveal.css'" in text:
        import re

        return re.sub(
            r'(<link[^>]+href=["\'][^"\']*nsc-reveal\.css["\'][^>]*/?>)',
            r"\1\n" + link,
            text,
            count=1,
        )
    if "</head>" in text:
        return text.replace("</head>", link + "\n</head>", 1)
    return text


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    href = rel_href(path, CHROME_CSS)
    new_text = ensure_chrome_link(text, href)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed = 0
    for fp in sorted(ROOT.rglob("*.html")):
        if "node_modules" in fp.parts or ".firecrawl" in fp.parts:
            continue
        if fp.parent == ROOT / "scripts":
            continue
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"Patched {changed} HTML file(s) with site-chrome.css")


if __name__ == "__main__":
    main()
