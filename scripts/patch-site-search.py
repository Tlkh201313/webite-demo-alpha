"""Wire site search form, script, and search results page."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD_SEARCH = """<div class="hidden lg:flex items-center rounded-full px-4 py-1.5 border border-outline-variant bg-white/10 transition-colors focus-within:bg-white/20 focus-within:border-white/40">
<span class="material-symbols-outlined text-on-primary/70 text-sm mr-2">search</span>
<input class="bg-transparent border-none focus:ring-0 text-body-md w-32 placeholder:text-on-primary/70 text-on-primary transition-all focus:w-48" placeholder="Search..." type="text"/>
</div>"""

NEW_SEARCH = """<form class="nsc-site-search nsc-site-search--header" role="search" data-nsc-site-search>
<label class="nsc-site-search__label">Search site</label>
<span class="material-symbols-outlined nsc-site-search__icon" aria-hidden="true">search</span>
<input class="nsc-site-search__input" type="search" name="q" placeholder="Search site…" autocomplete="off" enterkeyhint="search" aria-label="Search site"/>
<button type="submit" class="nsc-site-search__submit" aria-label="Search">
<span class="material-symbols-outlined" aria-hidden="true">arrow_forward</span>
</button>
</form>"""

SEARCH_PAGE_INPUT = """<form class="nsc-site-search nsc-site-search--page" role="search" data-nsc-site-search action="search.html" method="get">
<label class="nsc-site-search__label" for="nsc-search-page-input">Search site</label>
<span class="material-symbols-outlined nsc-site-search__icon" aria-hidden="true">search</span>
<input class="nsc-site-search__input" id="nsc-search-page-input" type="search" name="q" placeholder="Search pages, subjects, staff…" autocomplete="off" enterkeyhint="search"/>
<button type="submit" class="nsc-site-search__submit" aria-label="Search">
<span class="material-symbols-outlined" aria-hidden="true">arrow_forward</span>
</button>
</form>"""

SEARCH_BODY = f"""<!-- Search -->
<section class="nsc-search-page py-section-padding bg-surface">
<div class="max-w-container-max mx-auto px-gutter">
<div class="nsc-search-page__intro">
<h1 class="font-display-lg text-display-lg text-royal-purple mb-3">Search</h1>
<p class="font-body-md text-body-md text-on-surface-variant mb-6" id="nsc-search-summary">Enter a keyword to search pages, subjects, and staff.</p>
{SEARCH_PAGE_INPUT}
</div>
<p class="nsc-search-empty" id="nsc-search-empty" hidden>No pages matched your search. Try a shorter phrase or another keyword.</p>
<ul class="nsc-search-list" id="nsc-search-list" aria-live="polite"></ul>
<div id="nsc-search-results"></div>
</div>
</section>"""


def rel_asset(from_file: Path, name: str) -> str:
    depth = len(from_file.relative_to(ROOT).parts) - 1
    return ("../" * depth) + name


def inject_script(text: str, path: Path) -> str:
    if "nsc-site-search.js" in text:
        return text
    script_src = rel_asset(path, "nsc-site-search.js")
    tag = f'<script src="{script_src}" defer></script>'
    match = re.search(r'(<script src="[^"]*nsc-secure-login\.js" defer></script>)', text)
    if match:
        return text.replace(match.group(1), match.group(1) + "\n" + tag, 1)
    match = re.search(r'(<script src="[^"]*nsc-responsive\.js" defer></script>)', text)
    if match:
        return text.replace(match.group(1), match.group(1) + "\n" + tag, 1)
    return text


def patch_html(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    original = text
    changes: list[str] = []

    if OLD_SEARCH in text:
        text = text.replace(OLD_SEARCH, NEW_SEARCH)
        changes.append("search form")

    updated = inject_script(text, path)
    if updated != text:
        text = updated
        changes.append("search script")

    if text != original:
        path.write_text(text, encoding="utf-8")
    return changes


def build_search_page() -> None:
    template = ROOT / "contact-us.html"
    html = template.read_text(encoding="utf-8")
    html = html.replace(
        "<title>Contact Us | Northstowe Secondary College</title>",
        "<title>Search | Northstowe Secondary College</title>",
    )
    html = html.replace(
        '<a class="font-cta-text text-cta-text hover:text-lavender-tint transition-all duration-200 text-on-primary nav-link-underline min-[48em]:nav-link-underline bg-white/15" href="contact-us.html" aria-current="page">Contact Us</a>',
        '<a class="font-cta-text text-cta-text hover:text-lavender-tint transition-all duration-200 text-on-primary nav-link-underline min-[48em]:nav-link-underline" href="contact-us.html">Contact Us</a>',
    )
    html = re.sub(
        r"<!-- Banner -->.*?<!-- Footer -->",
        SEARCH_BODY + "\n<!-- Footer -->",
        html,
        count=1,
        flags=re.S,
    )
    if "nsc-site-search.js" not in html:
        html = inject_script(html, ROOT / "search.html")
    (ROOT / "search.html").write_text(html, encoding="utf-8")


def main() -> None:
    touched = 0
    for path in sorted(ROOT.rglob("*.html")):
        if "mobile-app" in path.parts or path.name == "search.html":
            continue
        changes = patch_html(path)
        if changes:
            touched += 1
            print(f"{path.relative_to(ROOT)}: {', '.join(changes)}")
    build_search_page()
    print(f"Patched {touched} HTML file(s); wrote search.html")


if __name__ == "__main__":
    main()
