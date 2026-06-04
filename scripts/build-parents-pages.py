"""
Fetch live Northstowe Parents and Carers pages and generate static HTML.
Patches the Parents dropdown in every site HTML file.
"""
from __future__ import annotations

import html as html_lib
import re
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.northstowesc.org"
TEMPLATE = ROOT / "learning" / "homework-prep.html"
PARENTS_DIR = ROOT / "parents-and-carers"

SSL_CTX = ssl.create_default_context()


def normalize_banner_url(url: str) -> str:
    url = html_lib.unescape(url or "").replace("&#038;", "&").strip()
    if not url:
        return "https://i0.wp.com/www.northstowesc.org/wp-content/uploads/2025/04/Banner-14.png?resize=1200,266&ssl=1"
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        url = f"https://www.northstowesc.org{url}"
    origin = url.split("?")[0]
    if "northstowesc.org" in origin and "i0.wp.com" not in origin:
        path = origin.split("northstowesc.org", 1)[1]
        return f"https://i0.wp.com/www.northstowesc.org{path}?resize=1200,266&ssl=1"
    return url


def banner_origin_url(cdn_url: str) -> str:
    return cdn_url.replace("https://i0.wp.com/www.northstowesc.org", "https://www.northstowesc.org").split("?")[0]


def banner_img_tag(cdn_url: str) -> str:
    origin = banner_origin_url(cdn_url)
    return (
        f'<img alt="" class="nsc-inner-banner__img" width="1000" height="222" decoding="async" fetchpriority="high" '
        f'src="{cdn_url}" onerror="this.onerror=null;this.src=\'{origin}\'"/>'
    )

# (output path under ROOT, live URL path, sidebar active slug)
PAGES: list[tuple[str, str, str]] = [
    ("parents-and-carers/index.html", "/parents-and-carers/", "index"),
    ("parents-and-carers/admissions.html", "/parents-and-carers/admissions/", "admissions"),
    (
        "parents-and-carers/applying-for-free-school-meals.html",
        "/parents-and-carers/applying-for-free-school-meals/",
        "applying-for-free-school-meals",
    ),
    ("parents-and-carers/bromcom.html", "/bromcom/", "bromcom"),
    (
        "parents-and-carers/early-closure-notification.html",
        "/parents-and-carers/early-closure-notification/",
        "early-closure-notification",
    ),
    (
        "parents-and-carers/home-school-communication.html",
        "/parents-and-carers/home-school-communication/",
        "home-school-communication",
    ),
    (
        "parents-and-carers/keeping-children-safe-online.html",
        "/parents-and-carers/keeping-children-safe-online/",
        "keeping-children-safe-online",
    ),
    ("parents-and-carers/open-evening.html", "/parents-and-carers/open-evening/", "open-evening"),
    ("parents-and-carers/parents-forum.html", "/parents-and-carers/parents-forum/", "parents-forum"),
    ("parents-and-carers/pupil-premium.html", "/parents-and-carers/pupil-premium/", "pupil-premium"),
    (
        "parents-and-carers/support-your-childs-learning.html",
        "/parents-and-carers/support-your-childs-learning/",
        "support-your-childs-learning",
    ),
    ("parents-and-carers/transition.html", "/parents-and-carers/transition/", "transition"),
]

PARENTS_SIDEBAR = [
    ("admissions", "Admissions", "parents-and-carers/admissions.html"),
    (
        "applying-for-free-school-meals",
        "Applying for Free School Meals",
        "parents-and-carers/applying-for-free-school-meals.html",
    ),
    ("bromcom", "Bromcom/MCAS", "parents-and-carers/bromcom.html"),
    (
        "early-closure-notification",
        "Early Closure Notification",
        "parents-and-carers/early-closure-notification.html",
    ),
    (
        "home-school-communication",
        "Home School Communication",
        "parents-and-carers/home-school-communication.html",
    ),
    (
        "keeping-children-safe-online",
        "Keeping Children Safe Online",
        "parents-and-carers/keeping-children-safe-online.html",
    ),
    ("open-evening", "NSC Open Evening 2025", "parents-and-carers/open-evening.html"),
    ("parents-forum", "Parents Forum", "parents-and-carers/parents-forum.html"),
    (
        "pupil-premium",
        "Pupil Premium and Meridian Trust Charter",
        "parents-and-carers/pupil-premium.html",
    ),
    (
        "support-your-childs-learning",
        "Supporting Your Child's Learning",
        "parents-and-carers/support-your-childs-learning.html",
    ),
    ("transition", "Transition", "parents-and-carers/transition.html"),
]


def _rel(from_file: Path, site_path: str) -> str:
    target = ROOT / site_path
    return Path(__import__("os").path.relpath(target, from_file.parent)).as_posix()


def fetch(url_path: str) -> str:
    url = BASE + url_path
    req = urllib.request.Request(url, headers={"User-Agent": "nsc-web-builder/1.0"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_page(raw: str) -> dict:
    title_m = re.search(r'<h1[^>]*class="[^"]*entry-title[^"]*"[^>]*>(.*?)</h1>', raw, re.I | re.S)
    title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else "Page"
    title = html_lib.unescape(title)

    banner_m = re.search(
        r'banner-title[^>]*>\s*([^<]+?)\s*</h1>\s*<img[^>]+src="([^"]+)"',
        raw,
        re.I | re.S,
    )
    if not banner_m:
        img_m = re.search(r'<img[^>]+class="[^"]*banner[^"]*"[^>]+src="([^"]+)"', raw, re.I)
        lazy = re.search(r'data-lazy-src="([^"]+)"', raw[raw.find("banner-title") : raw.find("banner-title") + 2000] if "banner-title" in raw else raw, re.I)
        banner_title, banner_src = title, ""
        if lazy:
            banner_src = html_lib.unescape(lazy.group(1)).replace("&#038;", "&").split("?")[0]
        elif img_m:
            banner_src = img_m.group(1)
    else:
        banner_title = html_lib.unescape(banner_m.group(1).strip())
        banner_src = banner_m.group(2)
        if "data:image" in banner_src or not banner_src:
            lazy = re.search(
                r'data-lazy-src="([^"]+)"',
                raw[max(0, raw.find(banner_m.group(0)) - 200) : raw.find(banner_m.group(0)) + 800],
                re.I,
            )
            if lazy:
                banner_src = html_lib.unescape(lazy.group(1)).replace("&#038;", "&").split("?")[0]

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
    return {
        "title": title,
        "banner_title": banner_title or title,
        "banner_src": banner_src,
        "entry_content": entry_content,
    }


def fix_lazy_images(content: str) -> str:
    def fix_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        lazy_src = re.search(r'data-lazy-src="([^"]*)"', tag, re.I)
        lazy_srcset = re.search(r'data-lazy-srcset="([^"]*)"', tag, re.I)
        lazy_sizes = re.search(r'data-lazy-sizes="([^"]*)"', tag, re.I)

        if lazy_src:
            src = html_lib.unescape(lazy_src.group(1)).replace("&#038;", "&").split("?")[0]
            if re.search(r'\ssrc="', tag, re.I):
                tag = re.sub(r'\ssrc="[^"]*"', f' src="{src}"', tag, count=1, flags=re.I)
            else:
                tag = re.sub(r"<img\b", f'<img src="{src}"', tag, count=1, flags=re.I)

        if lazy_srcset:
            srcset = html_lib.unescape(lazy_srcset.group(1)).replace("&#038;", "&")
            tag = re.sub(r'\ssrcset="[^"]*"', f' srcset="{srcset}"', tag, count=1, flags=re.I)
        elif re.search(r'\ssrcset="data:image/gif', tag, re.I):
            tag = re.sub(r'\ssrcset="[^"]*"', "", tag, count=1, flags=re.I)

        if lazy_sizes:
            sizes = html_lib.unescape(lazy_sizes.group(1))
            if re.search(r'\ssizes="', tag, re.I):
                tag = re.sub(r'\ssizes="[^"]*"', f' sizes="{sizes}"', tag, count=1, flags=re.I)
            else:
                tag = re.sub(r"<img\b", f'<img sizes="{sizes}"', tag, count=1, flags=re.I)

        tag = re.sub(r'\sdata-lazy-[^=]+="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r'\sdata-recalc-dims="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r"\sjetpack-lazy-image\b", "", tag, flags=re.I)
        tag = re.sub(r"[?&]is-pending-load=1", "", tag)
        tag = re.sub(r'\sclass="\s*"', "", tag)
        return tag

    return re.sub(r"<img\b[^>]*>", fix_img, content, flags=re.I)


def fix_content_links(content: str) -> str:
    content = re.sub(
        r'href="https://www\.northstowesc\.org(/[^"]*)"',
        lambda m: f'href="{m.group(1)}"' if m.group(1).startswith("/parents-and-carers") or m.group(1) == "/bromcom/" else m.group(0),
        content,
    )
    replacements = [
        (r'href="/parents-and-carers/"', 'href="/parents-and-carers/index.html"'),
        (r'href="/bromcom/"', 'href="/parents-and-carers/bromcom.html"'),
        (r'href="/parents-and-carers/admissions/"', 'href="/parents-and-carers/admissions.html"'),
        (r'href="/parents-and-carers/applying-for-free-school-meals/"', 'href="/parents-and-carers/applying-for-free-school-meals.html"'),
        (r'href="/parents-and-carers/early-closure-notification/"', 'href="/parents-and-carers/early-closure-notification.html"'),
        (r'href="/parents-and-carers/home-school-communication/"', 'href="/parents-and-carers/home-school-communication.html"'),
        (r'href="/parents-and-carers/keeping-children-safe-online/"', 'href="/parents-and-carers/keeping-children-safe-online.html"'),
        (r'href="/parents-and-carers/open-evening/"', 'href="/parents-and-carers/open-evening.html"'),
        (r'href="/parents-and-carers/parents-forum/"', 'href="/parents-and-carers/parents-forum.html"'),
        (r'href="/parents-and-carers/pupil-premium/"', 'href="/parents-and-carers/pupil-premium.html"'),
        (r'href="/parents-and-carers/support-your-childs-learning/"', 'href="/parents-and-carers/support-your-childs-learning.html"'),
        (r'href="/parents-and-carers/transition/"', 'href="/parents-and-carers/transition.html"'),
        (r'href="/learning/curriculum/"', 'href="/learning/curriculum.html"'),
        (r'href="/learning/enrichment/"', 'href="/learning/enrichment.html"'),
        (r'href="/learning/homework-prep/"', 'href="/learning/homework-prep.html"'),
        (r'href="/learning/examinations/"', 'href="/learning/examinations.html"'),
        (r'href="/parents-and-carers/pupil-premium/"', 'href="/parents-and-carers/pupil-premium.html"'),
    ]
    for pat, rep in replacements:
        content = re.sub(pat, rep, content)
    content = re.sub(
        r'href="/learning/([^"/]+)/"',
        lambda m: f'href="/learning/{m.group(1)}.html"',
        content,
    )
    return content


def sidebar_html(from_file: Path, active: str) -> str:
    lines = ['<p class="nsc-page-sidebar__parent">Parents and Carers</p>', '<nav aria-label="Parents and Carers">']
    for slug, label, site_path in PARENTS_SIDEBAR:
        href = _rel(from_file, site_path)
        cur = ' aria-current="page"' if slug == active else ""
        lines.append(f'<a href="{href}"{cur}>{html_lib.escape(label)}</a>')
    lines.append("</nav>")
    return "\n".join(lines)


def css_href(from_file: Path) -> str:
    return _rel(from_file, "parents-and-carers/parents-content.css")


def patch_chrome_paths(page: str, from_file: Path) -> str:
    page = re.sub(r'href="(?:\.\./)*main\.html"', f'href="{_rel(from_file, "main.html")}"', page)
    page = re.sub(r'href="(?:\.\./)*welcome\.html"', f'href="{_rel(from_file, "welcome.html")}"', page)
    pf = "../" * (len(from_file.relative_to(ROOT).parts) - 1)
    page = re.sub(r'href="(?:\.\./)+about/', f'href="{pf}about/', page)
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
    return page


def prepare_template(page: str, from_file: Path) -> str:
    href = css_href(from_file)
    page = re.sub(
        r'<link rel="stylesheet" href="[^"]*learning-content\.css"/>',
        f'<link rel="stylesheet" href="{href}"/>',
        page,
        count=1,
    )
    page = page.replace("<!-- Main content + Learning sidebar -->", "<!-- Main content + Parents sidebar -->")
    page = page.replace('aria-label="Learning section"', 'aria-label="Parents section"')
    return page


def build_page(out_rel: str, url_path: str, active: str) -> None:
    from_file = ROOT / out_rel
    template = TEMPLATE.read_text(encoding="utf-8")
    page = prepare_template(template, from_file)

    print(f"  fetch {url_path}")
    parsed = parse_page(fetch(url_path))
    title = parsed["title"]
    banner_src = normalize_banner_url(parsed["banner_src"])

    page = re.sub(r"<title>[^<]+</title>", f"<title>{html_lib.escape(title)} | Northstowe Secondary College</title>", page, count=1)

    page = re.sub(
        r'<h1 class="nsc-inner-banner__title">[^<]*</h1>',
        f'<h1 class="nsc-inner-banner__title">{html_lib.escape(parsed["banner_title"])}</h1>',
        page,
        count=1,
    )
    page = re.sub(
        r'<img alt="" class="nsc-inner-banner__img"[^>]*/>',
        banner_img_tag(banner_src),
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

    sb = sidebar_html(from_file, active if active != "index" else "")
    page = re.sub(
        r'<aside class="nsc-page-sidebar"[^>]*>.*?</aside>',
        f'<aside class="nsc-page-sidebar" aria-label="Parents section">\n{sb}\n</aside>',
        page,
        count=1,
        flags=re.S,
    )

    page = patch_chrome_paths(page, from_file)
    page = page.replace('aria-current="page" class="bg-white/15">Testimonials', ">Testimonials")
    page = re.sub(r' testaments\.html" aria-current="page"', ' testimonials.html"', page)

    from_file.parent.mkdir(parents=True, exist_ok=True)
    from_file.write_text(page, encoding="utf-8")
    print(f"  wrote {out_rel}")


def nav_parents_block(from_file: Path, current: str | None = None) -> str:
    def L(site_path: str) -> str:
        return _rel(from_file, site_path)

    def ac(site_path: str) -> str:
        if current and site_path == current:
            return ' aria-current="page" class="bg-white/15"'
        return ""

    items = "\n".join(
        f'<li><a href="{L(p)}"{ac(p)}>{html_lib.escape(lbl)}</a></li>'
        for _, lbl, p in PARENTS_SIDEBAR
    )
    trigger = L("parents-and-carers/index.html")
    return f"""<div class="relative nav-menu-item">
<a class="nav-trigger font-cta-text text-cta-text hover:text-lavender-tint flex items-center gap-1 transition-all text-on-primary" href="{trigger}">Parents and Carers<span class="material-symbols-outlined text-lg nav-chevron-desktop" aria-hidden="true">expand_more</span></a>
<ul class="nav-dropdown-panel">
{items}
</ul>
</div>"""


def patch_learning_nav_on_parents() -> None:
    """Clear Homework (PREP) active state copied from the learning page template."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_learning_pages",
        ROOT / "scripts" / "build-learning-pages.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)

    pattern = re.compile(
        r'<div class="relative nav-menu-item">\s*'
        r'<a class="nav-trigger[^"]*" href="[^"]*">Learning.*?</ul>\s*</div>\s*'
        r'(?=<div class="relative nav-menu-item">\s*<a class="nav-trigger[^"]*" href="[^"]*">(?:NSC Life|Parents))',
        re.S,
    )
    for fp in sorted(PARENTS_DIR.rglob("*.html")):
        text = fp.read_text(encoding="utf-8")
        new_block = mod.nav_learning_block(fp, None)
        new_text, n = pattern.subn(new_block + "\n", text, count=1)
        if n:
            fp.write_text(new_text, encoding="utf-8")
            print(f"  learning nav {fp.relative_to(ROOT)}")


def patch_nsc_life_nav_on_parents() -> None:
    """Ensure Parents pages include the full NSC Life dropdown between Learning and Parents."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_nsc_life_pages",
        ROOT / "scripts" / "build-nsc-life-pages.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)

    refresh_pattern = re.compile(
        r'<div class="relative nav-menu-item">\s*'
        r'<a class="nav-trigger[^"]*" href="[^"]*">NSC Life.*?</ul>\s*</div>\s*'
        r'(?=<div class="relative nav-menu-item">\s*<a class="nav-trigger[^"]*" href="[^"]*">Parents)',
        re.S,
    )
    insert_pattern = re.compile(
        r'(<div class="relative nav-menu-item">\s*'
        r'<a class="nav-trigger[^"]*" href="[^"]*">Learning.*?</ul>\s*</div>\s*)'
        r'(?=<div class="relative nav-menu-item">\s*<a class="nav-trigger[^"]*" href="[^"]*">Parents)',
        re.S,
    )

    for fp in sorted(PARENTS_DIR.rglob("*.html")):
        text = fp.read_text(encoding="utf-8")
        new_block = mod.nav_nsc_life_block(fp, None)
        if ">NSC Life<span" in text:
            new_text, n = refresh_pattern.subn(new_block + "\n", text, count=1)
        else:
            new_text, n = insert_pattern.subn(r"\1" + new_block + "\n", text, count=1)
        if n:
            fp.write_text(new_text, encoding="utf-8")
            print(f"  nsc life nav {fp.relative_to(ROOT)}")


def patch_all_nav() -> None:
    pattern = re.compile(
        r'<div class="relative nav-menu-item">\s*'
        r'<a class="nav-trigger[^"]*" href="[^"]*">Parents and Carers.*?</ul>\s*</div>\s*'
        r'(?=<div class="relative nav-menu-item">\s*<a class="nav-trigger[^"]*" href="[^"]*">News)',
        re.S,
    )
    for fp in ROOT.rglob("*.html"):
        text = fp.read_text(encoding="utf-8")
        if ">Parents and Carers<span" not in text:
            continue
        current = None
        try:
            rel = fp.relative_to(ROOT).as_posix()
            if rel.startswith("parents-and-carers/"):
                current = rel
        except ValueError:
            pass
        new_block = nav_parents_block(fp, current)
        new_text, n = pattern.subn(new_block + "\n", text, count=1)
        if n:
            fp.write_text(new_text, encoding="utf-8")
            print(f"  nav {fp.relative_to(ROOT)}")


def optimize_parents() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "optimize_learning_pages",
        ROOT / "scripts" / "optimize-learning-pages.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)

    for fp in sorted(PARENTS_DIR.rglob("*.html")):
        original = fp.read_text(encoding="utf-8")
        text = original
        text = mod.ensure_preconnect(text)
        href = css_href(fp)
        parents_href = href.replace("learning-content.css", "parents-content.css")
        text = mod.ensure_stylesheet(text, parents_href)
        text = mod.dedupe_stylesheet_links(text)
        text = text.replace("learning-content.css", "parents-content.css")
        text = mod.fix_broken_css(text)
        text = mod.strip_entry_noscript(text)
        text = mod.lazy_load_media(text)
        text = mod.lazy_trust_logos(text)
        text = mod.apply_learning_motion_markup(text)
        text = mod.extend_reveal_observer(text)
        text = mod.harden_reveal_script(text)
        if text != original:
            fp.write_text(text, encoding="utf-8")
            print(f"  optimize {fp.relative_to(ROOT)}")


def main() -> None:
    if not (ROOT / "parents-and-carers" / "parents-content.css").exists():
        PARENTS_DIR.mkdir(parents=True, exist_ok=True)
        src_css = ROOT / "learning" / "learning-content.css"
        (PARENTS_DIR / "parents-content.css").write_text(
            src_css.read_text(encoding="utf-8").replace(
                "Learning section", "Parents and Carers section"
            ),
            encoding="utf-8",
        )

    print("Building parents-and-carers pages...")
    for out_rel, url_path, active in PAGES:
        build_page(out_rel, url_path, active)

    print("Fixing Learning nav on parents pages...")
    patch_learning_nav_on_parents()

    print("Inserting NSC Life nav on parents pages...")
    patch_nsc_life_nav_on_parents()

    print("Patching Parents nav site-wide...")
    patch_all_nav()

    print("Optimizing parents pages...")
    optimize_parents()
    print("Done.")


if __name__ == "__main__":
    main()
