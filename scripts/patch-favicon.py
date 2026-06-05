"""Inject NSC favicon link on all public HTML pages."""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAVICON = ROOT / "assets" / "images" / "nsc-favicon.png"

ICON_BLOCK_TEMPLATE = """<link rel="icon" type="image/png" href="{href}" sizes="32x32"/>
<link rel="apple-touch-icon" href="{href}"/>"""

FAVICON_MARKER = 'rel="icon"'


def rel_href(html_path: Path, asset: Path) -> str:
    return Path(os.path.relpath(asset, html_path.parent)).as_posix()


def ensure_favicon(text: str, href: str) -> str:
    if FAVICON_MARKER in text and "nsc-favicon.png" in text:
        return text
    if FAVICON_MARKER in text:
        text = re.sub(
            r'<link[^>]+rel=["\']icon["\'][^>]*/?>\s*',
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r'<link[^>]+rel=["\']apple-touch-icon["\'][^>]*/?>\s*',
            "",
            text,
            flags=re.IGNORECASE,
        )
    block = ICON_BLOCK_TEMPLATE.format(href=href)
    if "<title>" in text:
        return re.sub(
            r"(<title>[^<]*</title>)",
            r"\1\n" + block,
            text,
            count=1,
            flags=re.IGNORECASE,
        )
    if "</head>" in text:
        return text.replace("</head>", block + "\n</head>", 1)
    return text


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    href = rel_href(path, FAVICON)
    new_text = ensure_favicon(text, href)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    if not FAVICON.is_file():
        raise SystemExit(f"Missing favicon asset: {FAVICON}")
    changed = 0
    for fp in sorted(ROOT.rglob("*.html")):
        if (
            "node_modules" in fp.parts
            or ".firecrawl" in fp.parts
            or "graphify-out" in fp.parts
            or "mobile-app" in fp.parts
        ):
            continue
        if fp.parent == ROOT / "scripts":
            continue
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"Patched {changed} HTML file(s) with favicon")


if __name__ == "__main__":
    main()
