from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = (
    '<label class="nsc-site-search__label" for="nsc-site-search-q">Search site</label>\n'
    '<span class="material-symbols-outlined nsc-site-search__icon" aria-hidden="true">search</span>\n'
    '<input class="nsc-site-search__input" id="nsc-site-search-q" type="search" name="q" placeholder="Search site…" autocomplete="off" enterkeyhint="search"/>'
)
NEW = (
    '<label class="nsc-site-search__label">Search site</label>\n'
    '<span class="material-symbols-outlined nsc-site-search__icon" aria-hidden="true">search</span>\n'
    '<input class="nsc-site-search__input" type="search" name="q" placeholder="Search site…" autocomplete="off" enterkeyhint="search" aria-label="Search site"/>'
)

count = 0
for path in ROOT.rglob("*.html"):
    if "mobile-app" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    if OLD in text:
        path.write_text(text.replace(OLD, NEW), encoding="utf-8")
        count += 1
print(count)
