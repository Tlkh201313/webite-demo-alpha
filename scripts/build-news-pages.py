"""
Fetch live Northstowe News and Events pages and generate static HTML.
Patches the News and Events dropdown in every site HTML file.
Verifies wp-content image URLs after build.
"""
from __future__ import annotations

import html as html_lib
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.northstowesc.org"
TEMPLATE = ROOT / "learning" / "homework-prep.html"
NEWS_DIR = ROOT / "news-and-events"
CSS_NAME = "news-content.css"

SSL_CTX = ssl.create_default_context()

PAGES: list[tuple[str, str, str]] = [
    ("news-and-events/index.html", "/news-and-events/", "index"),
    ("news-and-events/calendar.html", "/news-and-events/calendar/", "calendar"),
    ("news-and-events/latest-news.html", "/news-and-events/latest-news/", "latest-news"),
    ("news-and-events/newsletters.html", "/newsletter/", "newsletters"),
    (
        "news-and-events/term-dates-2025-2026.html",
        "/news-and-events/term-dates-2025-2026/",
        "term-dates-2025-2026",
    ),
    (
        "news-and-events/term-dates-2026-2027.html",
        "/news-and-events/term-dates-2026-2027/",
        "term-dates-2026-2027",
    ),
    (
        "news-and-events/term-dates-2027-2028.html",
        "/news-and-events/term-dates-2027-2028/",
        "term-dates-2027-2028",
    ),
]

NEWS_SIDEBAR = [
    ("index", "News and Events", "news-and-events/index.html"),
    ("calendar", "Calendar and Key Dates", "news-and-events/calendar.html"),
    ("latest-news", "Latest News", "news-and-events/latest-news.html"),
    ("newsletters", "NSC Newsletters", "news-and-events/newsletters.html"),
    (
        "term-dates-2025-2026",
        "Term Dates 2025-2026",
        "news-and-events/term-dates-2025-2026.html",
    ),
    (
        "term-dates-2026-2027",
        "Term Dates 2026-2027",
        "news-and-events/term-dates-2026-2027.html",
    ),
    (
        "term-dates-2027-2028",
        "Term Dates 2027-2028",
        "news-and-events/term-dates-2027-2028.html",
    ),
]

IMG_FALLBACK_SCRIPT = """
        window.nscImgFallback = function (img) {
            const chain = (img.getAttribute('data-fallback-src') || '').split('|').filter(Boolean);
            if (!chain.length) return;
            img.onerror = null;
            img.src = chain.shift();
            if (chain.length) {
                img.setAttribute('data-fallback-src', chain.join('|'));
                img.onerror = function () { window.nscImgFallback(img); };
            }
        };
"""


def _rel(from_file: Path, site_path: str) -> str:
    target = ROOT / site_path
    return Path(__import__("os").path.relpath(target, from_file.parent)).as_posix()


def fetch(url_path: str) -> str:
    url = BASE + url_path
    req = urllib.request.Request(url, headers={"User-Agent": "nsc-web-builder/1.0"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=90) as resp:
        return resp.read().decode("utf-8", errors="replace")


def decode_text(value: str) -> str:
    if not value:
        return value
    text = html_lib.unescape(value)
    if "&#" in text:
        text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text.replace("\u00a0", " ")).strip()


def origin_url(url: str) -> str:
    url = html_lib.unescape(url).replace("&#038;", "&").strip()
    url = re.sub(
        r"https://i0\.wp\.com/www\.northstowesc\.org(/wp-content/uploads/[^?\s\"']+)",
        r"https://www.northstowesc.org\1",
        url,
    )
    return url.split("?")[0]


def scaled_path(path: str) -> str:
    if re.search(r"-scaled\.(jpe?g|png|webp)$", path, re.I):
        return path
    return re.sub(r"\.(jpe?g|png|webp)$", r"-scaled.\1", path, flags=re.I)


def cdn_upload_path(path: str) -> str:
    """Only staff GM-* photos need a -scaled file for Jetpack CDN resize."""
    if "/GM-" in path and not re.search(r"-scaled\.(jpe?g|png|webp)$", path, re.I):
        return scaled_path(path)
    return path


def cdn_resize(url: str, w: int, h: int | None = None) -> str:
    base = origin_url(url)
    path = base.split("northstowesc.org", 1)[1] if "northstowesc.org" in base else base
    cdn = f"https://i0.wp.com/www.northstowesc.org{cdn_upload_path(path)}"
    q = f"resize={w},{h}" if h else f"resize={w}"
    return f"{cdn}?{q}&ssl=1"


def banner_url(url: str) -> str:
    if not url:
        return "https://i0.wp.com/www.northstowesc.org/wp-content/uploads/2025/04/Banner-14.png?resize=1200,266&ssl=1"
    return cdn_resize(url, 1200, 266)


def image_fallback_chain(url: str, w: int, h: int | None) -> str:
    origin = origin_url(url)
    chain = [origin]
    if "northstowesc.org" in origin:
        upload_path = origin.split("northstowesc.org", 1)[1]
        scaled_origin = origin_url(
            f"https://www.northstowesc.org{cdn_upload_path(upload_path)}"
        )
        if scaled_origin != origin:
            chain.insert(0, scaled_origin)
    cdn = cdn_resize(url, w, h)
    return html_lib.escape("|".join(dict.fromkeys([cdn] + chain)))


def best_img_url(tag: str) -> str | None:
    lazy_srcset = re.search(r'data-lazy-srcset="([^"]*)"', tag, re.I)
    if lazy_srcset:
        srcset = html_lib.unescape(lazy_srcset.group(1)).replace("&#038;", "&")
        scaled = [p.strip().split()[0] for p in srcset.split(",") if "-scaled." in p]
        if scaled:
            return origin_url(scaled[-1])
        parts = [p.strip().split()[0] for p in srcset.split(",") if p.strip()]
        if parts:
            return origin_url(parts[-1])
    for attr in ("data-lazy-src", "data-src", "src"):
        m = re.search(rf'\s{attr}="([^"]*)"', tag, re.I)
        if not m:
            continue
        val = html_lib.unescape(m.group(1)).replace("&#038;", "&")
        if val and not val.startswith("data:image"):
            return origin_url(val)
    return None


def fix_lazy_images(content: str) -> str:
    def fix_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        url = best_img_url(tag)
        if not url or "northstowesc.org/wp-content" not in url:
            return tag

        primary = cdn_resize(url, 960, None)
        fallbacks = image_fallback_chain(url, 960, None)
        tag = re.sub(r'\ssrc="[^"]*"', "", tag, count=1, flags=re.I)
        tag = re.sub(r'\ssrcset="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r'\ssizes="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r'\sdata-lazy-[^=]+="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r'\sdata-recalc-dims="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r"\sjetpack-lazy-image\b", "", tag, flags=re.I)
        tag = re.sub(r"[?&]is-pending-load=1", "", tag)
        if re.search(r'\ssrc="', tag, re.I):
            tag = re.sub(r'\ssrc="[^"]*"', f' src="{primary}"', tag, count=1, flags=re.I)
        else:
            tag = re.sub(r"<img\b", f'<img src="{primary}"', tag, count=1, flags=re.I)
        if 'data-fallback-src="' not in tag:
            tag = re.sub(
                r"<img\b",
                f'<img data-fallback-src="{fallbacks}" '
                f'onerror="window.nscImgFallback&&window.nscImgFallback(this)"',
                tag,
                count=1,
                flags=re.I,
            )
        if 'decoding="async"' not in tag:
            tag = tag.replace("<img", '<img decoding="async"', 1)
        if not re.search(r'\bloading="', tag, re.I):
            tag = tag.replace("<img", '<img loading="lazy"', 1)
        return tag

    return re.sub(r"<img\b[^>]*>", fix_img, content, flags=re.I)


def decode_entities_in_content(content: str) -> str:
    def fix_text(match: re.Match[str]) -> str:
        return ">" + decode_text(match.group(1)) + "<"

    return re.sub(r">([^<]*(?:&#\d+;|&amp;#)[^<]*)<", fix_text, content)


def fix_content_links(content: str) -> str:
    content = re.sub(
        r'href="https://www\.northstowesc\.org(/news-and-events/[^"]*)"',
        lambda m: f'href="{m.group(1)}"',
        content,
    )
    content = re.sub(
        r'href="https://www\.northstowesc\.org(/newsletter/[^"]*)"',
        lambda m: f'href="{m.group(1)}"',
        content,
    )
    replacements = [
        (r'href="/news-and-events/"', 'href="/news-and-events/index.html"'),
        (r'href="/news-and-events/calendar/"', 'href="/news-and-events/calendar.html"'),
        (r'href="/news-and-events/latest-news/"', 'href="/news-and-events/latest-news.html"'),
        (r'href="/newsletter/"', 'href="/news-and-events/newsletters.html"'),
        (
            r'href="/news-and-events/term-dates-2025-2026/"',
            'href="/news-and-events/term-dates-2025-2026.html"',
        ),
        (
            r'href="/news-and-events/term-dates-2026-2027/"',
            'href="/news-and-events/term-dates-2026-2027.html"',
        ),
        (
            r'href="/news-and-events/term-dates-2027-2028/"',
            'href="/news-and-events/term-dates-2027-2028.html"',
        ),
        (r'href="/parents-and-carers/"', 'href="/parents-and-carers/index.html"'),
        (r'href="/learning/curriculum/"', 'href="/learning/curriculum.html"'),
    ]
    for pat, rep in replacements:
        content = re.sub(pat, rep, content)
    return content


def parse_page(raw: str) -> dict:
    title_m = re.search(r'<h1[^>]*class="[^"]*entry-title[^"]*"[^>]*>(.*?)</h1>', raw, re.I | re.S)
    title = decode_text(re.sub(r"<[^>]+>", "", title_m.group(1)).strip()) if title_m else "Page"

    banner_m = re.search(
        r'banner-title[^>]*>\s*([^<]+?)\s*</h1>\s*<img[^>]+src="([^"]+)"',
        raw,
        re.I | re.S,
    )
    banner_title, banner_src = title, ""
    if banner_m:
        banner_title = decode_text(banner_m.group(1).strip())
        banner_src = banner_m.group(2)
        if "data:image" in banner_src or not banner_src:
            lazy = re.search(
                r'data-lazy-src="([^"]+)"',
                raw[max(0, raw.find(banner_m.group(0)) - 200) : raw.find(banner_m.group(0)) + 800],
                re.I,
            )
            if lazy:
                banner_src = html_lib.unescape(lazy.group(1)).replace("&#038;", "&")
    else:
        img_m = re.search(r'<img[^>]+class="[^"]*banner[^"]*"[^>]+src="([^"]+)"', raw, re.I)
        if img_m:
            banner_src = img_m.group(1)

    content_m = re.search(
        r'<div class="entry-content">(.*)</div>\s*</div>\s*</div>\s*</div>\s*<div class="widget-area',
        raw,
        re.I | re.S,
    )
    if not content_m:
        content_m = re.search(
            r'<div class="entry-content">(.*?)</div>\s*<!--\s*\.entry-content',
            raw,
            re.I | re.S,
        )
    if not content_m:
        content_m = re.search(r'<div class="entry-content">(.*?)</div>\s*</article>', raw, re.I | re.S)
    entry_content = content_m.group(1).strip() if content_m else "<p>Content unavailable.</p>"

    entry_content = re.sub(r'\s*<div class="sharedaddy.*', "", entry_content, flags=re.S)
    entry_content = fix_content_links(entry_content)
    entry_content = fix_lazy_images(entry_content)
    entry_content = decode_entities_in_content(entry_content)
    return {
        "title": title,
        "banner_title": banner_title or title,
        "banner_src": origin_url(banner_src) if banner_src else "",
        "entry_content": entry_content,
    }


def sidebar_html(from_file: Path, active: str) -> str:
    lines = [
        '<p class="nsc-page-sidebar__parent">News and Events</p>',
        '<nav aria-label="News and Events">',
    ]
    for slug, label, site_path in NEWS_SIDEBAR:
        href = _rel(from_file, site_path)
        cur = ' aria-current="page"' if slug == active else ""
        lines.append(f'<a href="{href}"{cur}>{html_lib.escape(label)}</a>')
    lines.append("</nav>")
    return "\n".join(lines)


def css_href(from_file: Path) -> str:
    return _rel(from_file, f"news-and-events/{CSS_NAME}")


def patch_chrome_paths(page: str, from_file: Path) -> str:
    page = re.sub(r'href="(?:\.\./)*main\.html"', f'href="{_rel(from_file, "main.html")}"', page)
    page = re.sub(r'href="(?:\.\./)*welcome\.html"', f'href="{_rel(from_file, "welcome.html")}"', page)
    depth = len(from_file.relative_to(ROOT).parts) - 1
    pf = "../" * depth if depth else ""
    page = re.sub(r'href="(?:\.\./)+about/', f'href="{pf}about/', page)
    page = re.sub(r'href="(?:\.\./)+learning/', f'href="{pf}learning/', page)
    page = re.sub(r'href="(?:\.\./)+parents-and-carers/', f'href="{pf}parents-and-carers/', page)
    page = re.sub(r'href="(?:\.\./)+nsc-life/', f'href="{pf}nsc-life/', page)
    learning_trigger = _rel(from_file, "learning/curriculum.html")
    page = re.sub(
        r'(<a class="nav-trigger[^"]*" href=")[^"]*(">Learning)',
        rf"\1{learning_trigger}\2",
        page,
        count=1,
    )
    parents_trigger = _rel(from_file, "parents-and-carers/index.html")
    page = re.sub(
        r'(<a class="nav-trigger[^"]*" href=")[^"]*(">Parents and Carers)',
        rf"\1{parents_trigger}\2",
        page,
        count=1,
    )
    nsc_trigger = _rel(from_file, "nsc-life/index.html") if (ROOT / "nsc-life" / "index.html").exists() else "#"
    page = re.sub(
        r'(<a class="nav-trigger[^"]*" href=")[^"]*(">NSC Life)',
        rf"\1{nsc_trigger}\2",
        page,
        count=1,
    )
    news_trigger = _rel(from_file, "news-and-events/index.html")
    page = re.sub(
        r'(<a class="nav-trigger[^"]*" href=")[^"]*(">News and Events)',
        rf"\1{news_trigger}\2",
        page,
        count=1,
    )
    return page


def prepare_template(page: str, from_file: Path) -> str:
    href = css_href(from_file)
    page = re.sub(
        r'<link rel="stylesheet" href="[^"]*learning-content\.css"/>',
        f'<link rel="stylesheet" href="{href}"/>',
        page,
        count=1,
    )
    page = page.replace("<!-- Main content + Learning sidebar -->", "<!-- Main content + News sidebar -->")
    page = page.replace('aria-label="Learning section"', 'aria-label="News and Events section"')
    return page


def build_page(out_rel: str, url_path: str, active: str) -> None:
    from_file = ROOT / out_rel
    page = prepare_template(TEMPLATE.read_text(encoding="utf-8"), from_file)

    print(f"  fetch {url_path}")
    parsed = parse_page(fetch(url_path))
    title = parsed["title"]
    banner_src = banner_url(parsed["banner_src"])

    page = re.sub(
        r"<title>[^<]+</title>",
        f"<title>{html_lib.escape(title)} | Northstowe Secondary College</title>",
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
        r'(<img alt="" class="nsc-inner-banner__img"[^>]+src=")[^"]+(")',
        rf"\1{banner_src}\2",
        page,
        count=1,
    )
    page = re.sub(
        r'(<img alt="" class="nsc-inner-banner__img")',
        r'\1 data-fallback-src="' + html_lib.escape(origin_url(parsed["banner_src"] or "")) + '" '
        r'onerror="window.nscImgFallback&&window.nscImgFallback(this)"',
        page,
        count=1,
    )

    main_block = f"""<header class="entry-header">
<h1 class="entry-title">{html_lib.escape(title)}</h1>
</header>
<div class="entry-content">
{parsed["entry_content"]}
</div>"""

    page = re.sub(
        r'<header class="entry-header">.*?</div>\s*</article>',
        main_block + "\n</article>",
        page,
        count=1,
        flags=re.S,
    )

    sb = sidebar_html(from_file, active)
    page = re.sub(
        r'<aside class="nsc-page-sidebar"[^>]*>.*?</aside>',
        f'<aside class="nsc-page-sidebar" aria-label="News and Events section">\n{sb}\n</aside>',
        page,
        count=1,
        flags=re.S,
    )

    page = patch_chrome_paths(page, from_file)
    from_file.parent.mkdir(parents=True, exist_ok=True)
    from_file.write_text(page, encoding="utf-8")
    print(f"  wrote {out_rel}")


def nav_news_block(from_file: Path, current: str | None = None) -> str:
    def L(site_path: str) -> str:
        return _rel(from_file, site_path)

    def ac(site_path: str) -> str:
        if current and site_path == current:
            return ' aria-current="page" class="bg-white/15"'
        return ""

    trigger = L("news-and-events/index.html")
    return f"""<div class="relative nav-menu-item">
<a class="nav-trigger font-cta-text text-cta-text hover:text-lavender-tint flex items-center gap-1 transition-all text-on-primary" href="{trigger}">News and Events<span class="material-symbols-outlined text-lg nav-chevron-desktop" aria-hidden="true">expand_more</span></a>
<ul class="nav-dropdown-panel">
<li><a href="{L("news-and-events/calendar.html")}"{ac("news-and-events/calendar.html")}>Calendar and Key Dates</a></li>
<li><a href="{L("news-and-events/latest-news.html")}"{ac("news-and-events/latest-news.html")}>Latest News</a></li>
<li><a href="{L("news-and-events/newsletters.html")}"{ac("news-and-events/newsletters.html")}>NSC Newsletters</a></li>
<li class="has-children">
<a href="#">Term Dates<span class="material-symbols-outlined sub-chevron">chevron_right</span></a>
<ul class="submenu-panel">
<li><a href="{L("news-and-events/term-dates-2025-2026.html")}"{ac("news-and-events/term-dates-2025-2026.html")}>Term Dates 2025-2026</a></li>
<li><a href="{L("news-and-events/term-dates-2026-2027.html")}"{ac("news-and-events/term-dates-2026-2027.html")}>Term Dates 2026-2027</a></li>
<li><a href="{L("news-and-events/term-dates-2027-2028.html")}"{ac("news-and-events/term-dates-2027-2028.html")}>Term Dates 2027-2028</a></li>
</ul>
</li>
</ul>
</div>"""


NEWS_NAV_PATTERN = re.compile(
    r'<div class="relative nav-menu-item">\s*'
    r'<a class="nav-trigger[^"]*" href="[^"]*">News and Events.*?</ul>\s*</div>\s*'
    r'(?=<a class="font-cta-text[^"]*" href="[^"]*">Hire Our Spaces)',
    re.S,
)


def patch_all_nav() -> None:
    for fp in ROOT.rglob("*.html"):
        text = fp.read_text(encoding="utf-8")
        if ">News and Events<span" not in text:
            continue
        current = None
        try:
            rel = fp.relative_to(ROOT).as_posix()
            if rel.startswith("news-and-events/"):
                current = rel
        except ValueError:
            pass
        new_block = nav_news_block(fp, current)
        new_text, n = NEWS_NAV_PATTERN.subn(new_block + "\n", text, count=1)
        if n:
            fp.write_text(new_text, encoding="utf-8")
            print(f"  nav {fp.relative_to(ROOT)}")


def optimize_news() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "optimize_learning_pages",
        ROOT / "scripts" / "optimize-learning-pages.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)

    for fp in sorted(NEWS_DIR.rglob("*.html")):
        original = fp.read_text(encoding="utf-8")
        text = original
        href = css_href(fp)
        text = mod.ensure_preconnect(text)
        text = mod.ensure_stylesheet(text, href)
        text = mod.dedupe_stylesheet_links(text)
        text = mod.fix_broken_css(text)
        text = mod.fix_wp_image_urls(text)
        text = mod.strip_entry_noscript(text)
        text = mod.lazy_load_media(text)
        text = mod.lazy_trust_logos(text)
        text = mod.optimize_banner_img(text)
        text = mod.apply_learning_motion_markup(text)
        text = mod.extend_reveal_observer(text)
        text = mod.harden_reveal_script(text)
        if "window.nscImgFallback" not in text:
            text = text.replace(
                "        const heroParallax = document.getElementById('hero-parallax');",
                IMG_FALLBACK_SCRIPT + "\n        const heroParallax = document.getElementById('hero-parallax');",
                1,
            )
        if text != original:
            fp.write_text(text, encoding="utf-8")
            print(f"  optimize {fp.relative_to(ROOT)}")


def verify_images() -> list[str]:
    """HEAD-check northstowesc wp-content images; try CDN + origin fallbacks."""
    failures: list[str] = []
    seen: set[str] = set()

    def check(url: str) -> bool:
        if url in seen:
            return True
        seen.add(url)
        if "northstowesc.org/wp-content" not in url and "i0.wp.com/www.northstowesc" not in url:
            return True
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "nsc-web-builder/1.0"})
        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=25) as resp:
                return resp.status < 400
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 404):
                return False
            return False
        except OSError:
            return False

    for fp in sorted(NEWS_DIR.rglob("*.html")):
        text = fp.read_text(encoding="utf-8")
        for match in re.finditer(
            r'(?:src|data-src|data-fallback-src)="([^"]+)"',
            text,
        ):
            raw = html_lib.unescape(match.group(1))
            for url in raw.split("|"):
                url = url.strip()
                if not url.startswith("http"):
                    continue
                if check(url):
                    continue
                origin = origin_url(url)
                if origin != url and check(origin):
                    continue
                if "northstowesc.org" in origin:
                    upload_path = origin.split("northstowesc.org", 1)[1]
                    scaled = origin_url(
                        f"https://www.northstowesc.org{cdn_upload_path(upload_path)}"
                    )
                    if scaled != origin and check(scaled):
                        continue
                failures.append(f"{fp.name}: {url}")
    return failures


def main() -> None:
    css_path = NEWS_DIR / CSS_NAME
    if not css_path.exists():
        NEWS_DIR.mkdir(parents=True, exist_ok=True)
        src_css = ROOT / "parents-and-carers" / "parents-content.css"
        css_path.write_text(
            src_css.read_text(encoding="utf-8").replace(
                "Parents and Carers section", "News and Events section"
            ),
            encoding="utf-8",
        )

    print("Building news-and-events pages...")
    for out_rel, url_path, active in PAGES:
        build_page(out_rel, url_path, active)

    print("Patching News nav site-wide...")
    patch_all_nav()

    print("Optimizing news pages...")
    optimize_news()

    print("Verifying images...")
    failures = verify_images()
    if failures:
        print(f"WARNING: {len(failures)} image URL(s) failed verification:")
        for line in failures[:20]:
            print(f"  - {line}")
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")
        raise SystemExit(1)
    print("All news page images verified OK.")
    print("Done.")


if __name__ == "__main__":
    main()
