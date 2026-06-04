"""Wire shared nsc-skeleton.css / nsc-skeleton.js and first-load skeleton markup."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_FILE = ROOT / "nsc-skeleton.css"
JS_FILE = ROOT / "nsc-skeleton.js"

CSS_LINK = '<link rel="stylesheet" href="{href}"/>'
JS_SCRIPT = '<script src="{href}"></script>'
SKELETON_MARKER = 'id="nsc-skeleton-loader"'

SKELETON_HTML = """<div id="nsc-skeleton-loader" class="nsc-skeleton" role="status" aria-live="polite" aria-busy="true" aria-label="Loading Northstowe Secondary College">
<div class="nsc-skeleton__page">
<div class="nsc-skeleton__alert nsc-skeleton__shimmer" aria-hidden="true"><span class="nsc-skeleton__alert-line"></span></div>
<header class="nsc-skeleton__masthead" aria-hidden="true">
<div class="nsc-skeleton__masthead-inner">
<div class="nsc-skeleton__masthead-row">
<div class="nsc-skeleton__logo nsc-skeleton__shimmer"></div>
<div class="nsc-skeleton__masthead-actions">
<div class="nsc-skeleton__menu-pill nsc-skeleton__shimmer"></div>
<div class="nsc-skeleton__search nsc-skeleton__shimmer"></div>
<div class="nsc-skeleton__cta nsc-skeleton__shimmer"></div>
</div>
</div>
<nav class="nsc-skeleton__nav" aria-hidden="true">
<span class="nsc-skeleton__nav-pill nsc-skeleton__nav-pill--sm nsc-skeleton__shimmer"></span>
<span class="nsc-skeleton__nav-pill nsc-skeleton__nav-pill--md nsc-skeleton__shimmer"></span>
<span class="nsc-skeleton__nav-pill nsc-skeleton__nav-pill--lg nsc-skeleton__shimmer"></span>
<span class="nsc-skeleton__nav-pill nsc-skeleton__nav-pill--xl nsc-skeleton__shimmer"></span>
<span class="nsc-skeleton__nav-pill nsc-skeleton__nav-pill--lg nsc-skeleton__shimmer"></span>
<span class="nsc-skeleton__nav-pill nsc-skeleton__nav-pill--md nsc-skeleton__shimmer"></span>
<span class="nsc-skeleton__nav-pill nsc-skeleton__nav-pill--sm nsc-skeleton__shimmer"></span>
</nav>
</div>
</header>
<section class="nsc-skeleton__banner" aria-hidden="true">
<div class="nsc-skeleton__banner-inner">
<div class="nsc-skeleton__banner-title nsc-skeleton__shimmer"></div>
</div>
<div class="nsc-skeleton__banner-img nsc-skeleton__shimmer"></div>
</section>
<section class="nsc-skeleton__hero-home" aria-hidden="true">
<div class="nsc-skeleton__hero-home-lines">
<span class="nsc-skeleton__shimmer"></span>
<span class="nsc-skeleton__shimmer"></span>
<span class="nsc-skeleton__shimmer"></span>
</div>
</section>
<section class="nsc-skeleton__content" aria-hidden="true">
<div class="nsc-skeleton__content-inner">
<div class="nsc-skeleton__layout">
<div class="nsc-skeleton__main">
<div class="nsc-skeleton__quick-bar">
<div class="nsc-skeleton__quick nsc-skeleton__shimmer"></div>
<div class="nsc-skeleton__quick nsc-skeleton__shimmer"></div>
</div>
<div class="nsc-skeleton__card nsc-skeleton__card--lavender">
<div class="nsc-skeleton__card-title nsc-skeleton__shimmer"></div>
<div class="nsc-skeleton__line nsc-skeleton__line--wide nsc-skeleton__shimmer"></div>
<div class="nsc-skeleton__line nsc-skeleton__line--medium nsc-skeleton__shimmer"></div>
<div class="nsc-skeleton__line nsc-skeleton__line--short nsc-skeleton__shimmer"></div>
</div>
<div class="nsc-skeleton__card">
<div class="nsc-skeleton__line nsc-skeleton__line--wide nsc-skeleton__shimmer"></div>
<div class="nsc-skeleton__line nsc-skeleton__line--medium nsc-skeleton__shimmer"></div>
</div>
</div>
<aside class="nsc-skeleton__sidebar nsc-skeleton__shimmer"></aside>
</div>
</div>
</section>
</div>
</div>
"""

BODY_OPEN_RE = re.compile(r"(<body[^>]*>\s*)", re.IGNORECASE)
SKELETON_BLOCK_RE = re.compile(
    r'<div id="nsc-skeleton-loader"[^>]*>.*?(?=<script src="[^"]*nsc-skeleton\.js"></script>)',
    re.DOTALL | re.IGNORECASE,
)
SKELETON_ORPHAN_RE = re.compile(
    r'\n?</div>\s*<div class="nsc-skeleton__hero nsc-skeleton__shimmer[^>]*>.*?</div>\s*</div>\s*\n',
    re.DOTALL | re.IGNORECASE,
)


def rel_href(html_path: Path, asset: Path) -> str:
    return Path(__import__("os").path.relpath(asset, html_path.parent)).as_posix()


def ensure_css_link(text: str, href: str) -> str:
    marker = f'href="{href}"'
    if marker in text:
        return text
    link = CSS_LINK.format(href=href)
    reveal_match = re.search(
        r'(<link rel="stylesheet" href="[^"]*nsc-reveal\.css"/>)',
        text,
    )
    if reveal_match:
        return text.replace(reveal_match.group(1), link + "\n" + reveal_match.group(1), 1)
    if "</head>" in text:
        return text.replace("</head>", link + "\n</head>", 1)
    return text


def ensure_skeleton_markup(text: str) -> str:
    if SKELETON_MARKER in text:
        return text

    def repl(match: re.Match[str]) -> str:
        return match.group(1) + SKELETON_HTML + "\n"

    return BODY_OPEN_RE.sub(repl, text, count=1)


def refresh_skeleton_markup(text: str) -> str:
    """Replace skeleton block up to nsc-skeleton.js (idempotent chrome layout)."""
    if SKELETON_MARKER not in text:
        return text
    text = SKELETON_ORPHAN_RE.sub("\n", text)
    if not SKELETON_BLOCK_RE.search(text):
        return text
    return SKELETON_BLOCK_RE.sub(SKELETON_HTML + "\n", text, count=1)


def ensure_js_script(text: str, href: str) -> str:
    marker = f'src="{href}"'
    if marker in text:
        return text
    script = JS_SCRIPT.format(href=href)
    if SKELETON_MARKER in text:
        chrome = re.search(r"\n<!-- Site chrome", text, re.IGNORECASE)
        if chrome:
            return text[: chrome.start()] + "\n" + script + text[chrome.start() :]
        if SKELETON_BLOCK_RE.search(text):
            return SKELETON_BLOCK_RE.sub(
                lambda m: m.group(0) + script + "\n",
                text,
                count=1,
            )
    if "</head>" in text:
        return text.replace("</head>", script + "\n</head>", 1)
    return text.replace("</body>", script + "\n</body>", 1)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    css_href = rel_href(path, CSS_FILE)
    js_href = rel_href(path, JS_FILE)
    text = ensure_css_link(text, css_href)
    text = ensure_skeleton_markup(text)
    text = refresh_skeleton_markup(text)
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
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"Patched {changed} HTML file(s)")


if __name__ == "__main__":
    main()
