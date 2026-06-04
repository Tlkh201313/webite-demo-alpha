"""
Fetch live Northstowe NSC Life pages and generate static HTML.
Patches the NSC Life dropdown across all site HTML files.
"""
from __future__ import annotations

import html as html_lib
import re
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.northstowesc.org"
TEMPLATE_TOP = ROOT / "learning" / "enrichment.html"
TEMPLATE_CHILD = ROOT / "learning" / "curriculum" / "celebrating-diversity.html"

_learning_spec = spec_from_file_location(
    "build_learning_pages",
    ROOT / "scripts" / "build-learning-pages.py",
)
_learning = module_from_spec(_learning_spec)
assert _learning_spec.loader is not None
sys.modules["build_learning_pages"] = _learning
_learning_spec.loader.exec_module(_learning)

fetch = _learning.fetch
parse_page = _learning.parse_page
_rel = _learning._rel
path_prefix = _learning.path_prefix
nav_learning_block = _learning.nav_learning_block

PAGES: list[tuple[str, str, str]] = [
    ("nsc-life/index.html", "/nsc-life/", "index"),
    ("nsc-life/absence.html", "/nsc-life/absence/", "absence"),
    ("nsc-life/attendance.html", "/nsc-life/attendance/", "attendance"),
    ("nsc-life/careers-education.html", "/nsc-life/careers-education/", "careers-education"),
    (
        "nsc-life/careers-education/careers-and-guidance-for-students.html",
        "/nsc-life/careers-education/careers-and-guidance-for-students/",
        "careers-students",
    ),
    (
        "nsc-life/careers-education/careers-and-guidance-for-parents.html",
        "/nsc-life/careers-education/careers-and-guidance-for-parents/",
        "careers-parents",
    ),
    (
        "nsc-life/careers-education/careers-and-guidance-for-teachers.html",
        "/nsc-life/careers-education/careers-and-guidance-for-teachers/",
        "careers-teachers",
    ),
    (
        "nsc-life/careers-education/information-for-employers.html",
        "/nsc-life/careers-education/information-for-employers/",
        "careers-employers",
    ),
    (
        "nsc-life/careers-education/labour-market-information.html",
        "/nsc-life/careers-education/labour-market-information/",
        "labour-market",
    ),
    (
        "nsc-life/careers-education/post-16-pathways.html",
        "/nsc-life/careers-education/post-16-pathways/",
        "post-16",
    ),
    (
        "nsc-life/careers-education/year-10-work-experience.html",
        "/nsc-life/careers-education/year-10-work-experience/",
        "work-experience",
    ),
    ("nsc-life/catering.html", "/nsc-life/catering/", "catering"),
    ("nsc-life/celebrating-achievement.html", "/nsc-life/celebrating-achievement/", "celebrating-achievement"),
    ("nsc-life/eal.html", "/nsc-life/eal/", "eal"),
    ("nsc-life/house-system.html", "/nsc-life/house-system/", "house-system"),
    ("nsc-life/house-system/attenborough.html", "/nsc-life/house-system/attenborough/", "attenborough"),
    ("nsc-life/house-system/dyson.html", "/nsc-life/house-system/dyson/", "dyson"),
    ("nsc-life/house-system/glennie.html", "/nsc-life/house-system/glennie/", "glennie"),
    ("nsc-life/house-system/parks.html", "/nsc-life/house-system/parks/", "parks"),
    ("nsc-life/library.html", "/nsc-life/library/", "library"),
    (
        "nsc-life/mental-health-wellbeing.html",
        "/nsc-life/mental-health-wellbeing/",
        "mental-health-wellbeing",
    ),
    (
        "nsc-life/feeling-worried-or-anxious.html",
        "/nsc-life/feeling-worried-or-anxious/",
        "feeling-worried",
    ),
    (
        "nsc-life/pastoral-care-and-safeguarding.html",
        "/nsc-life/pastoral-care-and-safeguarding/",
        "pastoral-care",
    ),
    (
        "nsc-life/pastoral-care-and-safeguarding/safeguarding-statement.html",
        "/nsc-life/pastoral-care-and-safeguarding/safeguarding-statement/",
        "safeguarding-statement",
    ),
    ("nsc-life/rewards-and-sanctions.html", "/nsc-life/rewards-and-sanctions/", "rewards-and-sanctions"),
    ("nsc-life/school-day.html", "/nsc-life/school-day/", "school-day"),
    ("nsc-life/send.html", "/nsc-life/send/", "send"),
    ("nsc-life/travel.html", "/nsc-life/travel/", "travel"),
    ("nsc-life/uniform.html", "/nsc-life/uniform/", "uniform"),
]

NSC_LIFE_SIDEBAR = [
    ("absence", "Absence", "nsc-life/absence.html"),
    ("attendance", "Attendance", "nsc-life/attendance.html"),
    ("careers-education", "Careers (CEIAG)", "nsc-life/careers-education.html"),
    ("catering", "Catering", "nsc-life/catering.html"),
    ("celebrating-achievement", "Celebrating Achievement", "nsc-life/celebrating-achievement.html"),
    ("eal", "EAL", "nsc-life/eal.html"),
    ("house-system", "House System", "nsc-life/house-system.html"),
    ("library", "Library", "nsc-life/library.html"),
    (
        "mental-health-wellbeing",
        "Mental Health &amp; Wellbeing",
        "nsc-life/mental-health-wellbeing.html",
    ),
    (
        "pastoral-care",
        "Pastoral Care and Safeguarding",
        "nsc-life/pastoral-care-and-safeguarding.html",
    ),
    ("rewards-and-sanctions", "Rewards and Sanctions", "nsc-life/rewards-and-sanctions.html"),
    ("school-day", "School Day", "nsc-life/school-day.html"),
    ("send", "SEND", "nsc-life/send.html"),
    ("travel", "Travel", "nsc-life/travel.html"),
    ("uniform", "Uniform", "nsc-life/uniform.html"),
]

CAREERS_SIDEBAR = [
    ("careers-students", "Careers and Guidance for Students", "nsc-life/careers-education/careers-and-guidance-for-students.html"),
    ("careers-parents", "Careers and Guidance for Parents", "nsc-life/careers-education/careers-and-guidance-for-parents.html"),
    ("careers-teachers", "Careers and Guidance for Teachers", "nsc-life/careers-education/careers-and-guidance-for-teachers.html"),
    ("careers-employers", "Information for Employers", "nsc-life/careers-education/information-for-employers.html"),
    ("labour-market", "Labour Market Information", "nsc-life/careers-education/labour-market-information.html"),
    ("post-16", "Post-16 Pathways", "nsc-life/careers-education/post-16-pathways.html"),
    ("work-experience", "Year 10 Work Experience", "nsc-life/careers-education/year-10-work-experience.html"),
]

HOUSE_SIDEBAR = [
    ("attenborough", "Attenborough", "nsc-life/house-system/attenborough.html"),
    ("dyson", "Dyson", "nsc-life/house-system/dyson.html"),
    ("glennie", "Glennie", "nsc-life/house-system/glennie.html"),
    ("parks", "Parks", "nsc-life/house-system/parks.html"),
]

CAREERS_SLUGS = {s[0] for s in CAREERS_SIDEBAR} | {"careers-education"}
HOUSE_SLUGS = {s[0] for s in HOUSE_SIDEBAR} | {"house-system"}
PASTORAL_SLUGS = {"pastoral-care", "safeguarding-statement"}
WELLBEING_SLUGS = {"mental-health-wellbeing", "feeling-worried"}


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


def fix_nsc_life_links(content: str) -> str:
    content = re.sub(
        r'href="https://www\.northstowesc\.org(/nsc-life/[^"]*)"',
        lambda m: f'href="{m.group(1)}"',
        content,
    )
    content = re.sub(r'href="/nsc-life/"', 'href="/nsc-life/index.html"', content)
    # Deepest paths first (careers + pastoral children)
    content = re.sub(
        r'href="/nsc-life/careers-education/([^"]+)/"',
        r'href="/nsc-life/careers-education/\1.html"',
        content,
    )
    content = re.sub(
        r'href="/nsc-life/house-system/([^"]+)/"',
        r'href="/nsc-life/house-system/\1.html"',
        content,
    )
    content = re.sub(
        r'href="/nsc-life/pastoral-care-and-safeguarding/([^"]+)/"',
        r'href="/nsc-life/pastoral-care-and-safeguarding/\1.html"',
        content,
    )
    content = re.sub(
        r'href="/nsc-life/([^"/]+)/"',
        lambda m: f'href="/nsc-life/{m.group(1)}.html"',
        content,
    )
    return content


def parse_nsc_page(url_path: str) -> dict:
    parsed = parse_page(fetch(url_path))
    parsed["entry_content"] = fix_nsc_life_links(parsed["entry_content"])
    return parsed


def is_nsc_child(out_path: str) -> bool:
    parts = Path(out_path).parts
    return len(parts) > 2 and parts[0] == "nsc-life"


def sidebar_html(from_file: Path, active: str, out_path: str) -> str:
    lines = ['<p class="nsc-page-sidebar__parent">NSC Life</p>', '<nav aria-label="NSC Life">']
    for slug, label, site_path in NSC_LIFE_SIDEBAR:
        href = _rel(from_file, site_path)
        cur = ' aria-current="page"' if slug == active else ""
        lines.append(f'<a href="{href}"{cur}>{label}</a>')
    lines.append("</nav>")

    if active in CAREERS_SLUGS:
        lines.append('<p class="nsc-page-sidebar__parent nsc-page-sidebar__parent--sub">Careers (CEIAG)</p>')
        lines.append('<nav aria-label="Careers">')
        mas = _rel(from_file, "nsc-life/careers-education.html")
        cur_parent = ' aria-current="page"' if active == "careers-education" else ""
        lines.append(f'<a href="{mas}"{cur_parent}>Careers (CEIAG)</a>')
        for slug, label, site_path in CAREERS_SIDEBAR:
            href = _rel(from_file, site_path)
            cur = ' aria-current="page"' if slug == active else ""
            lines.append(f'<a href="{href}"{cur}>{label}</a>')
        lines.append("</nav>")

    if active in HOUSE_SLUGS:
        lines.append('<p class="nsc-page-sidebar__parent nsc-page-sidebar__parent--sub">House System</p>')
        lines.append('<nav aria-label="House System">')
        mas = _rel(from_file, "nsc-life/house-system.html")
        cur_parent = ' aria-current="page"' if active == "house-system" else ""
        lines.append(f'<a href="{mas}"{cur_parent}>House System</a>')
        for slug, label, site_path in HOUSE_SIDEBAR:
            href = _rel(from_file, site_path)
            cur = ' aria-current="page"' if slug == active else ""
            lines.append(f'<a href="{href}"{cur}>{label}</a>')
        lines.append("</nav>")

    if active in WELLBEING_SLUGS:
        lines.append(
            '<p class="nsc-page-sidebar__parent nsc-page-sidebar__parent--sub">Mental Health &amp; Wellbeing</p>'
        )
        lines.append('<nav aria-label="Mental Health and Wellbeing">')
        mas = _rel(from_file, "nsc-life/mental-health-wellbeing.html")
        wor = _rel(from_file, "nsc-life/feeling-worried-or-anxious.html")
        cur_mh = ' aria-current="page"' if active == "mental-health-wellbeing" else ""
        cur_fw = ' aria-current="page"' if active == "feeling-worried" else ""
        lines.append(f'<a href="{mas}"{cur_mh}>Mental Health &amp; Wellbeing</a>')
        lines.append(f'<a href="{wor}"{cur_fw}>Feeling worried or anxious?</a>')
        lines.append("</nav>")

    if active in PASTORAL_SLUGS:
        lines.append(
            '<p class="nsc-page-sidebar__parent nsc-page-sidebar__parent--sub">Pastoral Care and Safeguarding</p>'
        )
        lines.append('<nav aria-label="Pastoral Care and Safeguarding">')
        mas = _rel(from_file, "nsc-life/pastoral-care-and-safeguarding.html")
        saf = _rel(from_file, "nsc-life/pastoral-care-and-safeguarding/safeguarding-statement.html")
        cur_pc = ' aria-current="page"' if active == "pastoral-care" else ""
        cur_sf = ' aria-current="page"' if active == "safeguarding-statement" else ""
        lines.append(f'<a href="{mas}"{cur_pc}>Pastoral Care and Safeguarding</a>')
        lines.append(f'<a href="{saf}"{cur_sf}>Safeguarding Statement</a>')
        lines.append("</nav>")

    return "\n".join(lines)


def patch_chrome_paths(page: str, from_file: Path) -> str:
    pf = path_prefix(from_file)
    page = re.sub(r'href="(?:\.\./)*main\.html"', f'href="{_rel(from_file, "main.html")}"', page)
    page = re.sub(r'href="(?:\.\./)*welcome\.html"', f'href="{_rel(from_file, "welcome.html")}"', page)
    page = re.sub(r'href="(?:\.\./)+about/', f'href="{pf}about/', page)
    learning_trigger = _rel(from_file, "learning/curriculum.html")
    page = re.sub(
        r'(<a class="nav-trigger[^"]*" href=")[^"]*(">Learning)',
        rf"\1{learning_trigger}\2",
        page,
        count=1,
    )
    nsc_trigger = _rel(from_file, "nsc-life/index.html")
    page = re.sub(
        r'(<a class="nav-trigger[^"]*" href=")[^"]*(">NSC Life)',
        rf"\1{nsc_trigger}\2",
        page,
        count=1,
    )
    return page


def build_page(out_rel: str, url_path: str, active: str) -> None:
    from_file = ROOT / out_rel
    template = TEMPLATE_CHILD.read_text(encoding="utf-8") if is_nsc_child(out_rel) else TEMPLATE_TOP.read_text(encoding="utf-8")

    print(f"  fetch {url_path}")
    parsed = parse_nsc_page(url_path)
    title = parsed["title"]
    banner_src = normalize_banner_url(parsed["banner_src"])

    page = template
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
        r'<img alt="" class="nsc-inner-banner__img"[^>]*/>',
        banner_img_tag(banner_src),
        page,
        count=1,
    )

    main_block = f"""<header class="entry-header">
<h1 class="entry-title">{html_lib.escape(title)}</h1>
</header>
<div class="entry-content learning-stagger">
{parsed["entry_content"]}
</div>"""

    page = re.sub(
        r'<header class="entry-header">.*?</div>\s*</article>',
        main_block + "\n</article>",
        page,
        count=1,
        flags=re.S,
    )

    sb = sidebar_html(from_file, active, out_rel)
    page = re.sub(
        r'<aside class="nsc-page-sidebar"[^>]*>.*?</aside>',
        f'<aside class="nsc-page-sidebar" aria-label="NSC Life section">\n{sb}\n</aside>',
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


def nav_nsc_life_block(from_file: Path, current: str | None = None) -> str:
    def L(site_path: str) -> str:
        return _rel(from_file, site_path)

    def ac(site_path: str) -> str:
        if current and site_path == current:
            return ' aria-current="page" class="bg-white/15"'
        return ""

    def li_children(label: str, href: str, children: str, site_self: str) -> str:
        ac_parent = ac(site_self)
        return f"""<li class="has-children">
<a href="{href}"{ac_parent}>{label}<span class="material-symbols-outlined sub-chevron">chevron_right</span></a>
<ul class="submenu-panel">
{children}
</ul>
</li>"""

    careers_children = "\n".join(
        f'<li><a href="{L(p)}"{ac(p)}>{lbl}</a></li>' for _, lbl, p in CAREERS_SIDEBAR
    )
    house_children = "\n".join(
        f'<li><a href="{L(p)}"{ac(p)}>{lbl}</a></li>' for _, lbl, p in HOUSE_SIDEBAR
    )

    items = [
        f'<li><a href="{L("nsc-life/absence.html")}"{ac("nsc-life/absence.html")}>Absence</a></li>',
        f'<li><a href="{L("nsc-life/attendance.html")}"{ac("nsc-life/attendance.html")}>Attendance</a></li>',
        li_children(
            "Careers (CEIAG)",
            L("nsc-life/careers-education.html"),
            careers_children,
            "nsc-life/careers-education.html",
        ),
        f'<li><a href="{L("nsc-life/catering.html")}"{ac("nsc-life/catering.html")}>Catering</a></li>',
        f'<li><a href="{L("nsc-life/celebrating-achievement.html")}"{ac("nsc-life/celebrating-achievement.html")}>Celebrating Achievement</a></li>',
        f'<li><a href="{L("nsc-life/eal.html")}"{ac("nsc-life/eal.html")}>EAL</a></li>',
        li_children(
            "House System",
            L("nsc-life/house-system.html"),
            house_children,
            "nsc-life/house-system.html",
        ),
        f'<li><a href="{L("nsc-life/library.html")}"{ac("nsc-life/library.html")}>Library</a></li>',
        li_children(
            "Mental Health &amp; Wellbeing",
            L("nsc-life/mental-health-wellbeing.html"),
            f'<li><a href="{L("nsc-life/feeling-worried-or-anxious.html")}"{ac("nsc-life/feeling-worried-or-anxious.html")}>Feeling worried or anxious?</a></li>',
            "nsc-life/mental-health-wellbeing.html",
        ),
        li_children(
            "Pastoral Care and Safeguarding",
            L("nsc-life/pastoral-care-and-safeguarding.html"),
            f'<li><a href="{L("nsc-life/pastoral-care-and-safeguarding/safeguarding-statement.html")}"{ac("nsc-life/pastoral-care-and-safeguarding/safeguarding-statement.html")}>Safeguarding Statement</a></li>',
            "nsc-life/pastoral-care-and-safeguarding.html",
        ),
        f'<li><a href="{L("nsc-life/rewards-and-sanctions.html")}"{ac("nsc-life/rewards-and-sanctions.html")}>Rewards and Sanctions</a></li>',
        f'<li><a href="{L("nsc-life/school-day.html")}"{ac("nsc-life/school-day.html")}>School Day</a></li>',
        f'<li><a href="{L("nsc-life/send.html")}"{ac("nsc-life/send.html")}>SEND</a></li>',
        f'<li><a href="{L("nsc-life/travel.html")}"{ac("nsc-life/travel.html")}>Travel</a></li>',
        f'<li><a href="{L("nsc-life/uniform.html")}"{ac("nsc-life/uniform.html")}>Uniform</a></li>',
    ]

    trigger_href = L("nsc-life/index.html")
    panel = "\n".join(items)
    return f"""<div class="relative nav-menu-item">
<a class="nav-trigger font-cta-text text-cta-text hover:text-lavender-tint flex items-center gap-1 transition-all text-on-primary" href="{trigger_href}">NSC Life<span class="material-symbols-outlined text-lg nav-chevron-desktop" aria-hidden="true">expand_more</span></a>
<ul class="nav-dropdown-panel">
{panel}
</ul>
</div>"""


def patch_all_nav() -> None:
    pattern = re.compile(
        r'<div class="relative nav-menu-item">\s*'
        r'<a class="nav-trigger[^"]*" href="[^"]*">NSC Life.*?</ul>\s*</div>\s*'
        r'(?=<div class="relative nav-menu-item">\s*<a class="nav-trigger[^"]*" href="[^"]*">Parents)',
        re.S,
    )
    for fp in ROOT.rglob("*.html"):
        text = fp.read_text(encoding="utf-8")
        if ">NSC Life<span" not in text:
            continue
        current = None
        try:
            rel = fp.relative_to(ROOT).as_posix()
            if rel.startswith("nsc-life/"):
                current = rel
        except ValueError:
            pass
        new_block = nav_nsc_life_block(fp, current)
        new_text, n = pattern.subn(new_block + "\n", text, count=1)
        if n:
            fp.write_text(new_text, encoding="utf-8")
            print(f"  nav {fp.relative_to(ROOT)}")


def patch_main_wellbeing_banner() -> None:
    main = ROOT / "main.html"
    text = main.read_text(encoding="utf-8")
    old = 'href="https://www.northstowesc.org/nsc-life/feeling-worried-or-anxious/"'
    new = 'href="nsc-life/feeling-worried-or-anxious.html"'
    if old in text:
        main.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("  main.html wellbeing banner")


def main() -> None:
    print("Building NSC Life pages...")
    for out_rel, url_path, active in PAGES:
        build_page(out_rel, url_path, active)

    print("Patching NSC Life nav site-wide...")
    patch_all_nav()

    print("Refreshing Learning nav (unchanged URLs, relative paths)...")
    learning_pattern = re.compile(
        r'<div class="relative nav-menu-item">\s*'
        r'<a class="nav-trigger[^"]*" href="[^"]*">Learning.*?</ul>\s*</div>\s*'
        r'(?=<div class="relative nav-menu-item">\s*<a class="nav-trigger[^"]*" href="[^"]*">NSC Life)',
        re.S,
    )
    for fp in ROOT.rglob("*.html"):
        text = fp.read_text(encoding="utf-8")
        if ">Learning<span" not in text:
            continue
        current = None
        try:
            rel = fp.relative_to(ROOT).as_posix()
            if rel.startswith("learning/"):
                current = rel
        except ValueError:
            pass
        new_block = nav_learning_block(fp, current)
        new_text, n = learning_pattern.subn(new_block + "\n", text, count=1)
        if n:
            fp.write_text(new_text, encoding="utf-8")

    patch_main_wellbeing_banner()

    print("Optimizing NSC Life pages (images, lazy-load, shared CSS)...")
    opt_spec = spec_from_file_location(
        "optimize_nsc_life_pages",
        ROOT / "scripts" / "optimize-nsc-life-pages.py",
    )
    opt_mod = module_from_spec(opt_spec)
    assert opt_spec.loader is not None
    opt_spec.loader.exec_module(opt_mod)
    opt_mod.main()

    print("Done.")


if __name__ == "__main__":
    main()
