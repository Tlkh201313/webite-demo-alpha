"""
Fetch live Northstowe Learning pages and generate static HTML.
Also patches the Learning dropdown in every site HTML file.
"""
from __future__ import annotations

import html as html_lib
import re
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.northstowesc.org"
TEMPLATE_CHILD = ROOT / "learning" / "curriculum" / "celebrating-diversity.html"
TEMPLATE_TOP = ROOT / "learning" / "curriculum.html"

SSL_CTX = ssl.create_default_context()

# (output path under ROOT, live URL path after domain, sidebar active slug)
CUSTOM_PAGES = frozenset({"learning/curriculum/subjects.html"})

PAGES: list[tuple[str, str, str]] = [
    # curriculum children (skip celebrating-diversity — already built)
    ("learning/curriculum/keystage-3.html", "/learning/curriculum/keystage-3/", "keystage-3"),
    ("learning/curriculum/keystage-4.html", "/learning/curriculum/keystage-4/", "keystage-4"),
    ("learning/curriculum/pastoral.html", "/learning/curriculum/pastoral/", "pastoral"),
    # subjects.html is hand-designed; omit from batch regen (see CUSTOM_PAGES)
    ("learning/curriculum/year-8-9-options.html", "/learning/curriculum/year-8-9-options/", "year-8-9-options"),
    ("learning/curriculum/subjects/art.html", "/learning/curriculum/subjects/art/", "art"),
    ("learning/curriculum/subjects/computer-science.html", "/learning/curriculum/subjects/computer-science/", "computer-science"),
    ("learning/curriculum/subjects/dt.html", "/learning/curriculum/subjects/dt/", "dt"),
    ("learning/curriculum/subjects/english.html", "/learning/curriculum/subjects/english/", "english"),
    ("learning/curriculum/subjects/ethics.html", "/learning/curriculum/subjects/ethics/", "ethics"),
    ("learning/curriculum/subjects/food-nutrition.html", "/learning/curriculum/subjects/food-nutrition/", "food-nutrition"),
    ("learning/curriculum/subjects/french.html", "/learning/curriculum/subjects/french/", "french"),
    ("learning/curriculum/subjects/geography.html", "/learning/curriculum/subjects/geography/", "geography"),
    ("learning/curriculum/subjects/health-and-social-care.html", "/learning/curriculum/subjects/health-and-social-care/", "health-and-social-care"),
    ("learning/curriculum/subjects/history.html", "/learning/curriculum/subjects/history/", "history"),
    ("learning/curriculum/subjects/how-to-thrive.html", "/learning/curriculum/subjects/how-to-thrive/", "how-to-thrive"),
    ("learning/curriculum/subjects/maths.html", "/learning/curriculum/subjects/maths/", "maths"),
    ("learning/curriculum/subjects/pe-and-sports.html", "/learning/curriculum/subjects/pe-and-sports/", "pe-and-sports"),
    ("learning/curriculum/subjects/performing-arts.html", "/learning/curriculum/subjects/performing-arts/", "performing-arts"),
    ("learning/curriculum/subjects/science.html", "/learning/curriculum/subjects/science/", "science"),
    # top-level learning
    ("learning/enrichment.html", "/learning/enrichment/", "enrichment"),
    (
        "learning/enrichment/extending-the-boundaries-of-learning-learning-outside-the-classroom.html",
        "/learning/enrichment/extending-the-boundaries-of-learning-learning-outside-the-classroom/",
        "extending-boundaries",
    ),
    ("learning/enrichment/student-leadership.html", "/learning/enrichment/student-leadership/", "student-leadership"),
    ("learning/examinations.html", "/learning/examinations/", "examinations"),
    ("learning/examinations/access-arrangements.html", "/learning/examinations/access-arrangements/", "access-arrangements"),
    ("learning/year-11-masterclasses.html", "/year-11-masterclasses/", "year-11-masterclasses"),
    ("learning/homework-prep.html", "/learning/homework-prep/", "homework-prep"),
    ("learning/interventions.html", "/learning/interventions/", "interventions"),
    ("learning/progress-and-assessment.html", "/learning/progress-and-assessment/", "progress-and-assessment"),
    ("learning/remote-learning.html", "/learning/remote-learning/", "remote-learning"),
    ("learning/teaching-and-learning-strategy.html", "/learning/teaching-and-learning-strategy/", "teaching-and-learning-strategy"),
    ("learning/whole-school-fluency.html", "/learning/whole-school-fluency/", "whole-school-fluency"),
]

CURRICULUM_SIDEBAR = [
    ("curriculum", "Curriculum", "learning/curriculum.html"),
    ("celebrating-diversity", "Celebrating Diversity", "learning/curriculum/celebrating-diversity.html"),
    ("keystage-3", "Key Stage 3", "learning/curriculum/keystage-3.html"),
    ("keystage-4", "Key Stage 4", "learning/curriculum/keystage-4.html"),
    ("pastoral", "Pastoral", "learning/curriculum/pastoral.html"),
    ("subjects", "Subjects", "learning/curriculum/subjects.html"),
    ("year-8-9-options", "Year 8 / 9 Options", "learning/curriculum/year-8-9-options.html"),
]

SUBJECT_SIDEBAR = [
    ("art", "Art", "learning/curriculum/subjects/art.html"),
    ("computer-science", "Computer Science", "learning/curriculum/subjects/computer-science.html"),
    ("dt", "Design and Technology", "learning/curriculum/subjects/dt.html"),
    ("english", "English", "learning/curriculum/subjects/english.html"),
    ("ethics", "Ethics", "learning/curriculum/subjects/ethics.html"),
    ("food-nutrition", "Food Nutrition", "learning/curriculum/subjects/food-nutrition.html"),
    ("french", "French", "learning/curriculum/subjects/french.html"),
    ("geography", "Geography", "learning/curriculum/subjects/geography.html"),
    ("health-and-social-care", "Health and Social Care", "learning/curriculum/subjects/health-and-social-care.html"),
    ("history", "History", "learning/curriculum/subjects/history.html"),
    ("how-to-thrive", "How To Thrive", "learning/curriculum/subjects/how-to-thrive.html"),
    ("maths", "Maths", "learning/curriculum/subjects/maths.html"),
    ("pe-and-sports", "PE and Sports", "learning/curriculum/subjects/pe-and-sports.html"),
    ("performing-arts", "Performing Arts", "learning/curriculum/subjects/performing-arts.html"),
    ("science", "Science", "learning/curriculum/subjects/science.html"),
]

LEARNING_SIDEBAR = [
    ("curriculum", "Curriculum", "learning/curriculum.html"),
    ("enrichment", "Enrichment", "learning/enrichment.html"),
    ("examinations", "Examinations", "learning/examinations.html"),
    ("homework-prep", "Homework (PREP)", "learning/homework-prep.html"),
    ("interventions", "Interventions", "learning/interventions.html"),
    ("progress-and-assessment", "Progress and Assessment", "learning/progress-and-assessment.html"),
    ("remote-learning", "Remote Learning", "learning/remote-learning.html"),
    ("teaching-and-learning-strategy", "Teaching and Learning Strategy", "learning/teaching-and-learning-strategy.html"),
    ("whole-school-fluency", "Whole School Fluency", "learning/whole-school-fluency.html"),
    ("year-11-masterclasses", "Year 11 Masterclasses", "learning/year-11-masterclasses.html"),
]


def _rel(from_file: Path, site_path: str) -> str:
    target = ROOT / site_path
    return Path(
        __import__("os").path.relpath(target, from_file.parent)
    ).as_posix()


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
        banner_title, banner_src = title, (img_m.group(1) if img_m else "")
    else:
        banner_title = html_lib.unescape(banner_m.group(1).strip())
        banner_src = banner_m.group(2)

    content_m = re.search(
        r'<div class="entry-content">(.*)</div>\s*</div>\s*</div>\s*</div>\s*<div class="widget-area',
        raw,
        re.I | re.S,
    )
    if not content_m:
        content_m = re.search(r'<div class="entry-content">(.*?)</div>\s*<!--\s*\.entry-content', raw, re.I | re.S)
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
    """WordPress/Jetpack lazy images use a 1x1 gif srcset; static pages need real src/srcset."""

    def fix_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        lazy_src = re.search(r'data-lazy-src="([^"]*)"', tag, re.I)
        lazy_srcset = re.search(r'data-lazy-srcset="([^"]*)"', tag, re.I)
        lazy_sizes = re.search(r'data-lazy-sizes="([^"]*)"', tag, re.I)

        if lazy_src:
            src = html_lib.unescape(lazy_src.group(1)).replace("&#038;", "&")
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

    content = re.sub(r"<img\b[^>]*>", fix_img, content, flags=re.I)
    return content


def fix_content_links(content: str) -> str:
    content = re.sub(
        r'href="https://www\.northstowesc\.org(/[^"]*)"',
        lambda m: f'href="{m.group(1)}"' if m.group(1).startswith("/learning/") or m.group(1).startswith("/year-11") else m.group(0),
        content,
    )
    # Map live paths to static files
    replacements = [
        (r'href="/learning/curriculum/"', 'href="/learning/curriculum.html"'),
        (r'href="/learning/curriculum/celebrating-diversity/"', 'href="/learning/curriculum/celebrating-diversity.html"'),
        (r'href="/learning/curriculum/keystage-3/"', 'href="/learning/curriculum/keystage-3.html"'),
        (r'href="/learning/curriculum/keystage-4/"', 'href="/learning/curriculum/keystage-4.html"'),
        (r'href="/learning/curriculum/pastoral/"', 'href="/learning/curriculum/pastoral.html"'),
        (r'href="/learning/curriculum/subjects/"', 'href="/learning/curriculum/subjects.html"'),
        (r'href="/learning/curriculum/year-8-9-options/"', 'href="/learning/curriculum/year-8-9-options.html"'),
        (r'href="/learning/enrichment/"', 'href="/learning/enrichment.html"'),
        (r'href="/learning/examinations/"', 'href="/learning/examinations.html"'),
        (r'href="/learning/homework-prep/"', 'href="/learning/homework-prep.html"'),
        (r'href="/year-11-masterclasses/"', 'href="/learning/year-11-masterclasses.html"'),
    ]
    for pat, rep in replacements:
        content = re.sub(pat, rep, content)
    content = re.sub(
        r'href="/learning/curriculum/subjects/([^/]+)/"',
        r'href="/learning/curriculum/subjects/\1.html"',
        content,
    )
    content = re.sub(
        r'href="/learning/enrichment/([^"]+)/"',
        lambda m: f'href="/learning/enrichment/{m.group(1)}.html"',
        content,
    )
    content = re.sub(
        r'href="/learning/examinations/([^"]+)/"',
        lambda m: f'href="/learning/examinations/{m.group(1)}.html"',
        content,
    )
    content = re.sub(
        r'href="/learning/([^"/]+)/"',
        lambda m: f'href="/learning/{m.group(1)}.html"',
        content,
    )
    return content


def is_subject_slug(slug: str) -> bool:
    return slug in {s[0] for s in SUBJECT_SIDEBAR}


def is_curriculum_child(out_path: str, slug: str) -> bool:
    return out_path.startswith("learning/curriculum/") and slug != "curriculum"


def sidebar_html(from_file: Path, active: str, out_path: str) -> str:
    if is_curriculum_child(out_path, active) or active == "subjects" or is_subject_slug(active):
        parent = "Curriculum"
        lines = [f'<p class="nsc-page-sidebar__parent">{parent}</p>', '<nav aria-label="Curriculum">']
        for slug, label, site_path in CURRICULUM_SIDEBAR:
            href = _rel(from_file, site_path)
            cur = ' aria-current="page"' if slug == active else ""
            lines.append(f'<a href="{href}"{cur}>{label}</a>')
        lines.append("</nav>")
        if active == "subjects" or is_subject_slug(active):
            lines.append('<p class="nsc-page-sidebar__parent nsc-page-sidebar__parent--sub">Subjects</p>')
            lines.append('<nav aria-label="Subjects">')
            for slug, label, site_path in SUBJECT_SIDEBAR:
                href = _rel(from_file, site_path)
                cur = ' aria-current="page"' if slug == active else ""
                lines.append(f'<a href="{href}"{cur}>{label}</a>')
            lines.append("</nav>")
        return "\n".join(lines)

    lines = ['<p class="nsc-page-sidebar__parent">Learning</p>', '<nav aria-label="Learning">']
    for slug, label, site_path in LEARNING_SIDEBAR:
        href = _rel(from_file, site_path)
        cur = ' aria-current="page"' if slug == active else ""
        lines.append(f'<a href="{href}"{cur}>{html_lib.escape(label)}</a>')
    lines.append("</nav>")
    if active in ("extending-boundaries", "student-leadership"):
        lines.append('<p class="nsc-page-sidebar__parent nsc-page-sidebar__parent--sub">Enrichment</p>')
        lines.append('<nav aria-label="Enrichment">')
        ext = _rel(
            from_file,
            "learning/enrichment/extending-the-boundaries-of-learning-learning-outside-the-classroom.html",
        )
        stu = _rel(from_file, "learning/enrichment/student-leadership.html")
        cur_ext = ' aria-current="page"' if active == "extending-boundaries" else ""
        cur_stu = ' aria-current="page"' if active == "student-leadership" else ""
        lines.append(f'<a href="{ext}"{cur_ext}>Extending the Boundaries of Learning</a>')
        lines.append(f'<a href="{stu}"{cur_stu}>Student Leadership</a>')
        lines.append("</nav>")
    if active == "access-arrangements":
        lines.append('<p class="nsc-page-sidebar__parent nsc-page-sidebar__parent--sub">Examinations</p>')
        lines.append('<nav aria-label="Examinations">')
        mas = _rel(from_file, "learning/year-11-masterclasses.html")
        acc = _rel(from_file, "learning/examinations/access-arrangements.html")
        lines.append(f'<a href="{mas}">Year 11 Masterclasses</a>')
        lines.append(f'<a href="{acc}" aria-current="page">Access Arrangements</a>')
        lines.append("</nav>")
    return "\n".join(lines)


def path_prefix(from_file: Path) -> str:
    depth = len(from_file.relative_to(ROOT).parts) - 1
    return "../" * depth if depth else ""


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
    return page


def build_page(out_rel: str, url_path: str, active: str) -> None:
    from_file = ROOT / out_rel
    is_top = not out_rel.startswith("learning/curriculum/")
    template = TEMPLATE_TOP.read_text(encoding="utf-8") if is_top else TEMPLATE_CHILD.read_text(encoding="utf-8")

    print(f"  fetch {url_path}")
    parsed = parse_page(fetch(url_path))
    title = parsed["title"]
    banner_src = parsed["banner_src"] or "https://www.northstowesc.org/wp-content/uploads/2025/04/Banner-14.png"

    page = template
    page = re.sub(r"<title>[^<]+</title>", f"<title>{html_lib.escape(title)} | Northstowe Secondary College</title>", page, count=1)

    page = re.sub(
        r'<h1 class="nsc-inner-banner__title">[^<]*</h1>',
        f'<h1 class="nsc-inner-banner__title">{html_lib.escape(parsed["banner_title"])}</h1>',
        page,
        count=1,
    )
    page = re.sub(
        r'(<img alt="" class="nsc-inner-banner__img"[^>]+src=")[^"]+(")',
        rf'\1{banner_src}\2',
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
        r"<header class=\"entry-header\">.*?</div>\s*</article>",
        main_block + "\n</article>",
        page,
        count=1,
        flags=re.S,
    )

    sb = sidebar_html(from_file, active, out_rel)
    page = re.sub(
        r'<aside class="nsc-page-sidebar"[^>]*>.*?</aside>',
        f'<aside class="nsc-page-sidebar" aria-label="{"Curriculum" if is_curriculum_child(out_rel, active) or is_subject_slug(active) else "Learning"} section">\n{sb}\n</aside>',
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


def nav_learning_block(from_file: Path, current: str | None = None) -> str:
    """Full Learning dropdown for header; current = site path of active page or None."""

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

    subjects = "\n".join(
        f'<li><a href="{L(p)}"{ac(p)}>{lbl}</a></li>' for _, lbl, p in SUBJECT_SIDEBAR
    )
    curriculum_children = f"""<li><a href="{L("learning/curriculum/celebrating-diversity.html")}"{ac("learning/curriculum/celebrating-diversity.html")}>Celebrating Diversity</a></li>
<li><a href="{L("learning/curriculum/keystage-3.html")}"{ac("learning/curriculum/keystage-3.html")}>Key Stage 3</a></li>
<li><a href="{L("learning/curriculum/keystage-4.html")}"{ac("learning/curriculum/keystage-4.html")}>Key Stage 4</a></li>
<li><a href="{L("learning/curriculum/pastoral.html")}"{ac("learning/curriculum/pastoral.html")}>Pastoral</a></li>
{li_children("Subjects", L("learning/curriculum/subjects.html"), subjects, "learning/curriculum/subjects.html")}
<li><a href="{L("learning/curriculum/year-8-9-options.html")}"{ac("learning/curriculum/year-8-9-options.html")}>Year 8 / 9 Options</a></li>"""

    enrichment_children = f"""<li><a href="{L("learning/enrichment/extending-the-boundaries-of-learning-learning-outside-the-classroom.html")}"{ac("learning/enrichment/extending-the-boundaries-of-learning-learning-outside-the-classroom.html")}>Extending the Boundaries of Learning</a></li>
<li><a href="{L("learning/enrichment/student-leadership.html")}"{ac("learning/enrichment/student-leadership.html")}>Student Leadership</a></li>"""

    exam_children = f"""<li><a href="{L("learning/year-11-masterclasses.html")}"{ac("learning/year-11-masterclasses.html")}>Year 11 Masterclasses</a></li>
<li><a href="{L("learning/examinations/access-arrangements.html")}"{ac("learning/examinations/access-arrangements.html")}>Access Arrangements</a></li>"""

    trigger_href = L("learning/curriculum.html")
    return f"""<div class="relative nav-menu-item">
<a class="nav-trigger font-cta-text text-cta-text hover:text-lavender-tint flex items-center gap-1 transition-all text-on-primary" href="{trigger_href}">Learning<span class="material-symbols-outlined text-lg nav-chevron-desktop" aria-hidden="true">expand_more</span></a>
<ul class="nav-dropdown-panel">
{li_children("Curriculum", L("learning/curriculum.html"), curriculum_children, "learning/curriculum.html")}
{li_children("Enrichment", L("learning/enrichment.html"), enrichment_children, "learning/enrichment.html")}
{li_children("Examinations", L("learning/examinations.html"), exam_children, "learning/examinations.html")}
<li><a href="{L("learning/homework-prep.html")}"{ac("learning/homework-prep.html")}>Homework (PREP)</a></li>
<li><a href="{L("learning/interventions.html")}"{ac("learning/interventions.html")}>Interventions</a></li>
<li><a href="{L("learning/progress-and-assessment.html")}"{ac("learning/progress-and-assessment.html")}>Progress and Assessment</a></li>
<li><a href="{L("learning/remote-learning.html")}"{ac("learning/remote-learning.html")}>Remote Learning</a></li>
<li><a href="{L("learning/teaching-and-learning-strategy.html")}"{ac("learning/teaching-and-learning-strategy.html")}>Teaching and Learning Strategy</a></li>
<li><a href="{L("learning/whole-school-fluency.html")}"{ac("learning/whole-school-fluency.html")}>Whole School Fluency</a></li>
</ul>
</div>"""


def patch_all_nav() -> None:
    pattern = re.compile(
        r'<div class="relative nav-menu-item">\s*'
        r'<a class="nav-trigger[^"]*" href="[^"]*">Learning.*?</ul>\s*</div>\s*'
        r'(?=<div class="relative nav-menu-item">\s*<a class="nav-trigger[^"]*" href="[^"]*">NSC Life)',
        re.S,
    )
    html_files = list(ROOT.rglob("*.html"))
    for fp in html_files:
        text = fp.read_text(encoding="utf-8")
        if ">Learning<span" not in text:
            continue
        # Guess current learning page from path
        current = None
        try:
            rel = fp.relative_to(ROOT).as_posix()
            if rel.startswith("learning/"):
                current = rel
        except ValueError:
            pass
        new_block = nav_learning_block(fp, current)
        new_text, n = pattern.subn(new_block + "\n", text, count=1)
        if n:
            fp.write_text(new_text, encoding="utf-8")
            print(f"  nav {fp.relative_to(ROOT)}")


def main() -> None:
    print("Building learning pages...")
    for out_rel, url_path, active in PAGES:
        if out_rel in CUSTOM_PAGES:
            continue
        build_page(out_rel, url_path, active)

    print("Refreshing celebrating-diversity...")
    build_page(
        "learning/curriculum/celebrating-diversity.html",
        "/learning/curriculum/celebrating-diversity/",
        "celebrating-diversity",
    )

    print("Refreshing curriculum.html content...")
    build_page("learning/curriculum.html", "/learning/curriculum/", "curriculum")

    print("Patching Learning nav site-wide...")
    patch_all_nav()

    from importlib import util as importlib_util

    spec = importlib_util.spec_from_file_location(
        "optimize_learning_pages",
        ROOT / "scripts" / "optimize-learning-pages.py",
    )
    mod = importlib_util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    mod.main()
    print("Done.")


if __name__ == "__main__":
    main()
