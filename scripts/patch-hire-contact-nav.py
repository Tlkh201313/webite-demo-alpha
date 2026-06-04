"""
Wire Hire Our Spaces to P&E Sports (external) and build local contact-us.html.
"""
from __future__ import annotations

import html as html_lib
import importlib.util
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "learning" / "homework-prep.html"
CONTACT_SOURCE = ROOT / ".firecrawl" / "contact-us-source.html"
CONTACT_CONTENT = ROOT / "scripts" / "contact-page-content.html"
HIRE_URL = "https://pandesports.com/northstowe-college"
MAP_EMBED_SRC = (
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d13807.721788538725!"
    "2d0.06222643582055764!3d52.28181828584326!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!"
    "4f13.1!3m3!1m2!1s0x47d875fd5c71448f%3A0x10922d5ccf5d4c75!"
    "2sNorthstowe%20secondary%20school!5e0!3m2!1sen!2suk!4v1578600948111!5m2!1sen!2suk"
)
MAP_OPEN_URL = (
    "https://www.google.com/maps/search/?api=1&query="
    "Northstowe+Secondary+College,+Stirling+Road,+Northstowe,+CB24+1DJ"
)

NEWS_MOD = importlib.util.module_from_spec(
    spec := importlib.util.spec_from_file_location(
        "build_news_pages", ROOT / "scripts" / "build-news-pages.py"
    )
)
assert spec and spec.loader
spec.loader.exec_module(NEWS_MOD)

PARENTS_MOD = importlib.util.module_from_spec(
    pspec := importlib.util.spec_from_file_location(
        "build_parents_pages", ROOT / "scripts" / "build-parents-pages.py"
    )
)
assert pspec and pspec.loader
pspec.loader.exec_module(PARENTS_MOD)


def _rel(from_file: Path, site_path: str) -> str:
    return Path(os.path.relpath(ROOT / site_path, from_file.parent)).as_posix()


def map_section_html() -> str:
    return f"""<section class="nsc-map-section" aria-label="College location on Google Maps">
<a class="nsc-map-section__open" href="{MAP_OPEN_URL}" target="_blank" rel="noopener noreferrer">
<span class="material-symbols-outlined" aria-hidden="true">open_in_new</span>
Open in Maps
</a>
<aside class="nsc-map-section__card" aria-label="Contact details">
<h2 class="nsc-map-section__card-title">Northstowe Secondary College</h2>
<div class="nsc-map-section__card-body">
<p class="nsc-map-section__label">Address:</p>
<address>
Northstowe Secondary College,<br>
Stirling Road,<br>
Northstowe,<br>
CB24 1DJ
</address>
<p>Telephone: <a href="tel:01223343800">01223 343800</a></p>
<p>Email: <a href="mailto:office@northstowesc.org">office@northstowesc.org</a></p>
</div>
</aside>
<iframe
class="nsc-map-section__iframe"
title="Northstowe Secondary College on Google Maps"
src="{MAP_EMBED_SRC}"
width="100%"
height="500"
loading="lazy"
referrerpolicy="no-referrer-when-downgrade"
allowfullscreen=""
></iframe>
</section>"""


def clean_contact_content(content: str) -> str:
    content = re.sub(
        r'<section class="section-map">.*?</section>\s*</section>',
        "",
        content,
        count=1,
        flags=re.S,
    )
    content = re.sub(r'\sstyle="width:-\d+px;height:-\d+px"', "", content)
    content = re.sub(
        r'href="https://www\.northstowesc\.org/about/our-staff/?"',
        'href="about/our-staff.html"',
        content,
    )
    content = re.sub(
        r'href="https://www\.northstowesc\.org/contact-us/?"',
        'href="contact-us.html"',
        content,
    )
    content = re.sub(r'href="http://01223 343800"', 'href="tel:01223343800"', content)
    return content


def contact_page_content() -> str:
    return CONTACT_CONTENT.read_text(encoding="utf-8").strip()


def build_contact_us() -> None:
    from_file = ROOT / "contact-us.html"
    raw = CONTACT_SOURCE.read_text(encoding="utf-8")
    parsed = NEWS_MOD.parse_page(raw)

    page = TEMPLATE.read_text(encoding="utf-8")
    page = re.sub(
        r'<link rel="stylesheet" href="[^"]*learning-content\.css"/>',
        '<link rel="stylesheet" href="learning/learning-content.css"/>\n'
        '<link rel="stylesheet" href="site-content.css"/>',
        page,
        count=1,
    )
    page = page.replace("<!-- Main content + Learning sidebar -->", "<!-- Main content -->")

    banner_cdn = PARENTS_MOD.normalize_banner_url(parsed["banner_src"])
    banner_tag = PARENTS_MOD.banner_img_tag(banner_cdn)

    page = re.sub(
        r"<title>[^<]+</title>",
        f"<title>{html_lib.escape(parsed['title'])} | Northstowe Secondary College</title>",
        page,
        count=1,
    )
    page = re.sub(
        r'<h1 class="nsc-inner-banner__title">[^<]*</h1>',
        f'<h1 class="nsc-inner-banner__title">{html_lib.escape(parsed["banner_title"])}</h1>',
        page,
        count=1,
    )
    page = re.sub(
        r'<img alt="" class="nsc-inner-banner__img"[^>]*/>',
        banner_tag,
        page,
        count=1,
    )

    main_block = (
        '<section class="py-section-padding bg-surface-container-lowest">\n'
        '<div class="max-w-container-max mx-auto px-4 sm:px-gutter">\n'
        f"{contact_page_content()}\n"
        "</div>\n"
        "</section>\n"
        f"{map_section_html()}"
    )

    page = re.sub(
        r'<section class="py-section-padding bg-surface-container-lowest">.*?</section>\s*<!-- Trust Partner Section -->',
        main_block + "\n<!-- Trust Partner Section -->",
        page,
        count=1,
        flags=re.S,
    )
    if "<!-- Main content -->" in page and "nsc-contact-page" not in page:
        page = re.sub(
            r'<!-- Main content -->.*?<section class="py-section-padding bg-surface-container-lowest">.*?</section>',
            f"<!-- Main content -->\n{main_block}",
            page,
            count=1,
            flags=re.S,
        )

    page = NEWS_MOD.patch_chrome_paths(page, from_file)
    page = patch_hire_contact_links(page, from_file, contact_current=True)
    from_file.write_text(page, encoding="utf-8")
    print("  wrote contact-us.html")


def patch_hire_contact_links(text: str, from_file: Path, contact_current: bool = False) -> str:
    contact_href = _rel(from_file, "contact-us.html")
    nav_classes = (
        "font-cta-text text-cta-text hover:text-lavender-tint transition-all duration-200 "
        "text-on-primary nav-link-underline min-[48em]:nav-link-underline"
    )
    if contact_current:
        nav_classes += " bg-white/15"
    aria = ' aria-current="page"' if contact_current else ""
    contact_nav = (
        f'<a class="{nav_classes}" href="{contact_href}"{aria}>Contact Us</a>'
    )

    text = re.sub(
        r'<a class="font-cta-text text-cta-text hover:text-lavender-tint transition-all duration-200 text-on-primary nav-link-underline min-\[48em\]:nav-link-underline" href="[^"]*">Hire Our Spaces</a>',
        f'<a class="font-cta-text text-cta-text hover:text-lavender-tint transition-all duration-200 text-on-primary nav-link-underline min-[48em]:nav-link-underline" href="{HIRE_URL}" target="_blank" rel="noopener noreferrer">Hire Our Spaces</a>',
        text,
        count=1,
    )
    text = re.sub(
        r'<a class="font-cta-text text-cta-text hover:text-lavender-tint transition-all duration-200 text-on-primary nav-link-underline min-\[48em\]:nav-link-underline" href="[^"]*">Contact Us</a>',
        contact_nav,
        text,
        count=1,
    )
    text = re.sub(
        r'href="https://www\.northstowesc\.org/contact-us/?"',
        f'href="{contact_href}"',
        text,
    )
    text = re.sub(
        r'(<a class="[^"]*" href=")[^"]*(">Contact Us</a>)',
        lambda m: m.group(1) + contact_href + m.group(2)
        if "font-cta-text" not in m.group(0) and "northstowesc.org" not in m.group(0)
        else m.group(0),
        text,
    )
    # Content placeholders still pointing at #
    text = re.sub(
        r'(<a class="text-trust-blue[^"]*" href=")[^"]*(">Contact Us</a>)',
        rf"\1{contact_href}\2",
        text,
    )
    text = re.sub(
        r'(<a class="font-body-md[^"]*" href=")[^"]*(">Contact Us</a>)',
        rf"\1{contact_href}\2",
        text,
    )
    return text


def patch_all() -> None:
    if not CONTACT_SOURCE.exists():
        raise SystemExit(f"Missing {CONTACT_SOURCE}. Run scripts/fetch-contact-us.py first.")

    print("Building contact-us.html...")
    build_contact_us()

    print("Patching Hire Our Spaces + Contact Us links...")
    count = 0
    for fp in sorted(ROOT.rglob("*.html")):
        if fp.name == "contact-us.html":
            continue
        if ".firecrawl" in fp.parts:
            continue
        original = fp.read_text(encoding="utf-8")
        updated = patch_hire_contact_links(original, fp)
        if updated != original:
            fp.write_text(updated, encoding="utf-8")
            print(f"  {fp.relative_to(ROOT)}")
            count += 1
    print(f"Patched {count} file(s).")


if __name__ == "__main__":
    patch_all()
