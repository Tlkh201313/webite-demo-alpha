"""Wire shared nsc-reveal.css / nsc-reveal.js and remove duplicated inline observer blocks."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_FILE = ROOT / "nsc-reveal.css"
JS_FILE = ROOT / "nsc-reveal.js"

CSS_LINK = '<link rel="stylesheet" href="{href}"/>'
JS_SCRIPT = '<script src="{href}" defer></script>'

REVEAL_DOM_REPLACEMENT = "\n    document.addEventListener('DOMContentLoaded', () => {\n"

# Standard block (flush + 1200ms safety reveal).
REVEAL_DOM_BLOCK_RE = re.compile(
    r"\n\s*// Intersection Observer for scroll animations\n"
    r"\s*document\.addEventListener\('DOMContentLoaded', \(\) => \{\n"
    r"\s*const observerOptions = \{.*?"
    r"\n\s*\}, 1200\);\n",
    re.DOTALL,
)

# Shorter variant (about pages, no safety timeout).
REVEAL_DOM_SHORT_RE = re.compile(
    r"\n\s*// Intersection Observer for scroll animations\n"
    r"\s*document\.addEventListener\('DOMContentLoaded', \(\) => \{\n"
    r"\s*const observerOptions = \{.*?"
    r"(?=\n\s*// Prototype nav:|\n\s*// Responsive nav:)",
    re.DOTALL,
)

# main.html: smaller observer inside existing DOMContentLoaded (before loadHomeNewsletters).
MAIN_REVEAL_RE = re.compile(
    r"\n\s*const observerOptions = \{.*?"
    r"revealElements\.forEach\(el => observer\.observe\(el\)\);\n",
    re.DOTALL,
)


def rel_href(html_path: Path, asset: Path) -> str:
    return Path(__import__("os").path.relpath(asset, html_path.parent)).as_posix()


def ensure_css_link(text: str, href: str) -> str:
    marker = f'href="{href}"'
    if marker in text:
        return text
    link = CSS_LINK.format(href=href)
    if "</head>" in text:
        return text.replace("</head>", link + "\n</head>", 1)
    return text


def ensure_js_script(text: str, href: str) -> str:
    marker = f'src="{href}"'
    if marker in text:
        return text
    script = JS_SCRIPT.format(href=href)
    fab = "<!-- FAB for Top -->"
    if fab in text:
        return text.replace(fab, script + "\n" + fab, 1)
    if "<script>" in text and "Intersection Observer" in text:
        return text.replace("<script>", script + "\n<script>", 1)
    return text.replace("</body>", script + "\n</body>", 1)


def strip_inline_reveal(text: str, path: Path) -> tuple[str, bool]:
    if path.name == "main.html":
        new_text, n = MAIN_REVEAL_RE.subn("\n", text, count=1)
        return new_text, n > 0

    new_text, n = REVEAL_DOM_BLOCK_RE.subn(REVEAL_DOM_REPLACEMENT, text, count=1)
    if n:
        return new_text, True
    new_text, n = REVEAL_DOM_SHORT_RE.subn(REVEAL_DOM_REPLACEMENT, text, count=1)
    return new_text, n > 0


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    css_href = rel_href(path, CSS_FILE)
    js_href = rel_href(path, JS_FILE)
    text = ensure_css_link(text, css_href)
    text = ensure_js_script(text, js_href)
    text, stripped = strip_inline_reveal(text, path)
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed = 0
    for fp in sorted(ROOT.rglob("*.html")):
        if "node_modules" in fp.parts or ".firecrawl" in fp.parts:
            continue
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"Patched {changed} HTML file(s)")


if __name__ == "__main__":
    main()
