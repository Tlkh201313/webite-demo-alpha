"""Generate about/our-staff.html from ofsted template + staff-data.json."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "about" / "ofsted-information.html"
DATA = ROOT / "about" / "staff-data.json"
OUT = ROOT / "about" / "our-staff.html"

data = json.loads(DATA.read_text(encoding="utf-8"))
page = TEMPLATE.read_text(encoding="utf-8")

page = page.replace(
    "<title>Ofsted Information | Northstowe Secondary College</title>",
    "<title>Our Staff | Northstowe Secondary College</title>",
)
page = page.replace('href="ofsted-information.html">About', 'href="our-staff.html">About')
page = page.replace(
    '<li><a href="ofsted-information.html" aria-current="page" class="bg-white/15">Ofsted Information</a></li>\n<li><a href="our-staff.html">Our Staff</a></li>',
    '<li><a href="ofsted-information.html">Ofsted Information</a></li>\n<li><a href="our-staff.html" aria-current="page" class="bg-white/15">Our Staff</a></li>',
)
HERO_IMG = "../assets/images/NSC-Banner-5-1c9bb89d90.jpg"
page = page.replace(
    'src="https://www.northstowesc.org/wp-content/uploads/2025/04/Banner-28.png"',
    f'src="{HERO_IMG}"',
)
page = page.replace(
    'src="https://www.northstowesc.org/wp-content/uploads/2022/10/NSC-Banner-5.jpg"',
    f'src="{HERO_IMG}"',
)
page = page.replace(
    """<h1 class="font-display-lg text-[clamp(2rem,6vw,3rem)] sm:text-display-lg text-on-primary mb-6 leading-tight opacity-0 animate-[fadeInUp_0.8s_ease-out_0.4s_forwards]">Ofsted Information</h1>
<p class="font-body-lg text-body-lg text-on-primary/90 mb-10 leading-relaxed opacity-0 animate-[fadeInUp_0.8s_ease-out_0.6s_forwards]">
                    Northstowe Secondary College received its first Ofsted inspection in March — read our report, ratings, and statutory website information.
                </p>
<div class="flex flex-wrap gap-4 opacity-0 animate-[fadeInUp_0.8s_ease-out_0.8s_forwards]">
<a class="bg-on-primary text-deep-plum font-cta-text text-cta-text px-8 py-4 flex items-center gap-2 hover:bg-lavender-tint transition-all duration-300 interactive-hover rounded-md" href="#inspection-report">
                        Inspection report
                        <span class="material-symbols-outlined">description</span>
</a>
<a class="border-2 border-on-primary text-on-primary font-cta-text text-cta-text px-8 py-4 hover:bg-on-primary hover:text-deep-plum transition-all duration-300 interactive-hover rounded-md" href="#website-requirements">
                        Website requirements
                    </a>
</div>""",
    """<h1 class="font-display-lg text-[clamp(2rem,6vw,3rem)] sm:text-display-lg text-on-primary mb-6 leading-tight opacity-0 animate-[fadeInUp_0.8s_ease-out_0.4s_forwards]">Our Staff</h1>
<p class="font-body-lg text-body-lg text-on-primary/90 mb-10 leading-relaxed opacity-0 animate-[fadeInUp_0.8s_ease-out_0.6s_forwards]">
                    Meet the people who make Northstowe Secondary College a kind, curious, and hardworking community — from senior leadership to teaching, support, and site teams.
                </p>
<div class="flex flex-wrap gap-4 opacity-0 animate-[fadeInUp_0.8s_ease-out_0.8s_forwards]">
<a class="bg-on-primary text-deep-plum font-cta-text text-cta-text px-8 py-4 flex items-center gap-2 hover:bg-lavender-tint transition-all duration-300 interactive-hover rounded-md" href="#senior-leadership">
                        Senior leadership
                        <span class="material-symbols-outlined">groups</span>
</a>
<a class="border-2 border-on-primary text-on-primary font-cta-text text-cta-text px-8 py-4 hover:bg-on-primary hover:text-deep-plum transition-all duration-300 interactive-hover rounded-md" href="#staff-directory">
                        Full directory
                    </a>
</div>""",
)

staff_css = """
            .staff-accordion {
                border-radius: 0.75rem;
                overflow: hidden;
                border: 1px solid rgba(73, 14, 103, 0.12);
                background: #ffffff;
                box-shadow: 0 4px 24px rgba(73, 14, 103, 0.06);
            }
            .staff-accordion + .staff-accordion { margin-top: 1rem; }
            .staff-accordion summary {
                list-style: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                padding: 1.125rem 1.5rem;
                background: #490e67;
                color: #ffffff;
                font-family: "Hanken Grotesk", sans-serif;
                font-size: 1.0625rem;
                font-weight: 600;
                letter-spacing: -0.01em;
                transition: background 0.2s ease;
            }
            .staff-accordion summary::-webkit-details-marker { display: none; }
            .staff-accordion summary::after {
                content: "add";
                font-family: "Material Symbols Outlined";
                font-size: 1.5rem;
                font-weight: 400;
                transition: transform 0.25s ease;
            }
            .staff-accordion[open] summary::after {
                content: "remove";
            }
            .staff-accordion[open] summary {
                border-bottom: 1px solid rgba(255, 255, 255, 0.15);
            }
            .staff-accordion__label {
                flex: 1;
                min-width: 0;
            }
            .staff-accordion__count {
                flex-shrink: 0;
                min-width: 3.25rem;
                text-align: right;
                font-size: inherit;
                line-height: 1;
                font-weight: 400;
                font-variant-numeric: tabular-nums;
                opacity: 0.85;
                align-self: center;
            }
            .staff-accordion__body {
                padding: 1.5rem;
            }
            .staff-lead-card {
                display: grid;
                grid-template-columns: minmax(120px, 160px) 1fr;
                gap: 1.5rem;
                padding: 1.5rem 0;
                border-bottom: 1px solid rgba(73, 14, 103, 0.1);
            }
            .staff-lead-card:last-child { border-bottom: none; padding-bottom: 0; }
            .staff-lead-card:first-child { padding-top: 0; }
            @media (max-width: 640px) {
                .staff-lead-card {
                    grid-template-columns: 1fr;
                }
            }
            .staff-lead-card__photo {
                aspect-ratio: 3/4;
                object-fit: cover;
                border-radius: 0.5rem;
                width: 100%;
                max-width: 160px;
                box-shadow: 0 8px 24px rgba(73, 14, 103, 0.12);
            }
            .staff-compact-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
                gap: 1rem;
            }
            .staff-compact-card {
                display: flex;
                gap: 0.875rem;
                align-items: flex-start;
                padding: 0.875rem;
                border-radius: 0.5rem;
                border: 1px solid rgba(73, 14, 103, 0.08);
                background: #faf8fb;
                transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
            }
            .staff-compact-card:hover {
                border-color: rgba(73, 14, 103, 0.2);
                box-shadow: 0 6px 16px rgba(73, 14, 103, 0.08);
                transform: translateY(-2px);
            }
            .staff-compact-card__photo {
                width: 56px;
                height: 72px;
                object-fit: cover;
                border-radius: 0.375rem;
                flex-shrink: 0;
                background: #e1e3e4;
            }
            .staff-compact-card__placeholder {
                width: 56px;
                height: 72px;
                border-radius: 0.375rem;
                flex-shrink: 0;
                background: linear-gradient(135deg, #e1e3e4, #f3ebf6);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #85419d;
            }
            .staff-email-note {
                border-left: 4px solid #490e67;
            }
"""

page = page.replace(
    "            #website-requirements-list.reveal-stagger-group.is-visible .reveal-stagger-child:nth-child(21)",
    staff_css + "\n            #website-requirements-list.reveal-stagger-group.is-visible .reveal-stagger-child:nth-child(21)",
    1,
)


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def text(s: str) -> str:
    """Decode entities from JSON/source, then escape for safe HTML text."""
    return esc(html.unescape(s or ""))


def staff_photo_url(url: str | None) -> str | None:
    """Use mirrored local assets; remote hotlinks break on GitHub Pages."""
    if not url:
        return None
    return url.split("?")[0].strip()


def roles_html(roles: list[str]) -> str:
    parts = []
    for r in roles:
        for line in r.split("\n"):
            line = line.strip()
            if line:
                parts.append(f"<span class=\"block text-on-surface-variant\">{text(line)}</span>")
    return "".join(parts)


def lead_card(m: dict, *, eager: bool = False) -> str:
    img = ""
    if m.get("image"):
        src = staff_photo_url(m["image"])
        load = (
            'loading="eager" fetchpriority="high" decoding="async"'
            if eager
            else 'loading="lazy" fetchpriority="low" decoding="async"'
        )
        img = (
            f'<img class="staff-lead-card__photo" src="{esc(src)}" alt="" {load} '
            f'width="160" height="213"/>'
        )
    else:
        img = '<div class="staff-lead-card__photo bg-lavender-tint flex items-center justify-center"><span class="material-symbols-outlined text-royal-purple text-4xl">person</span></div>'
    email = ""
    if m.get("email"):
        email = f'<a class="text-trust-blue hover:text-royal-purple font-medium underline mt-2 inline-block" href="mailto:{esc(m["email"])}">{esc(m["email"])}</a>'
    bio = ""
    if m.get("bio"):
        bio = f'<p class="font-body-md text-body-md text-on-surface-variant leading-relaxed mt-3">{text(m["bio"])}</p>'
    return f"""<article class="staff-lead-card reveal-stagger-child">
{img}
<div>
<h3 class="font-headline-md text-headline-md text-royal-purple">{text(m["name"])}</h3>
<div class="font-body-md text-body-md font-medium text-secondary mt-1">{roles_html(m.get("roles", []))}</div>
{email}
{bio}
</div>
</article>"""


def compact_card(m: dict, *, deferred: bool = True) -> str:
    photo = ""
    if m.get("image"):
        src = staff_photo_url(m["image"])
        if deferred:
            photo = (
                f'<img class="staff-compact-card__photo staff-photo--deferred" '
                f'data-src="{esc(src)}" alt="" width="56" height="72" loading="lazy" decoding="async"/>'
            )
        else:
            photo = (
                f'<img class="staff-compact-card__photo" src="{esc(src)}" alt="" '
                f'loading="lazy" decoding="async" width="56" height="72"/>'
            )
    else:
        photo = '<div class="staff-compact-card__placeholder" aria-hidden="true"><span class="material-symbols-outlined text-xl">person</span></div>'
    return f"""<div class="staff-compact-card reveal-stagger-child">
{photo}
<div class="min-w-0">
<p class="font-cta-text text-cta-text text-royal-purple leading-snug">{text(m["name"])}</p>
<div class="font-body-md text-body-md text-sm mt-0.5">{roles_html(m.get("roles", []))}</div>
</div>
</div>"""


sections_html = []
for sec in data:
    if "senior-leadership" in sec["id"]:
        continue
    sid = sec["id"]
    open_attr = ""
    inner = ""
    if sec["members"] and sec["members"][0].get("type") == "leadership":
        inner = f'<div class="reveal-stagger-group">{"".join(lead_card(m) for m in sec["members"])}</div>'
    else:
        cards = "".join(compact_card(m) for m in sec["members"])
        inner = f'<div class="staff-compact-grid reveal-stagger-group">{cards}</div>'
    count = len(sec["members"])
    sections_html.append(
        f"""<details class="staff-accordion reveal-on-scroll" id="{esc(sid)}"{open_attr}>
<summary><span class="staff-accordion__label">{esc(sec["title"])}</span><span class="staff-accordion__count">({count})</span></summary>
<div class="staff-accordion__body">{inner}</div>
</details>"""
    )

main_block = f"""<!-- Intro -->
<section class="py-section-padding bg-surface-container-lowest" id="staff-intro">
<div class="max-w-container-max mx-auto px-4 sm:px-gutter">
<div class="max-w-3xl mx-auto reveal-on-scroll">
<h2 class="font-headline-lg text-headline-lg text-royal-purple mb-stack-md"><span class="section-heading-line">Contacting our team</span></h2>
<p class="font-body-lg text-body-lg text-on-surface-variant leading-relaxed mb-stack-md">Please use the email system of <strong class="text-royal-purple">first initial + surname@northstowe.education</strong> to reach staff by email (for example, Jane Smith would be <a class="text-trust-blue hover:text-royal-purple font-medium underline" href="mailto:jsmith@northstowe.education">jsmith@northstowe.education</a>).</p>
<div class="staff-email-note rounded-xl bg-lavender-tint/60 p-6 flex gap-4 items-start">
<span class="material-symbols-outlined text-royal-purple text-3xl flex-shrink-0">mail</span>
<p class="font-body-md text-body-md text-on-surface-variant leading-relaxed">Senior leaders include direct email links below. For general enquiries, please use our <a class="text-trust-blue hover:text-royal-purple font-medium underline" href="#">Contact Us</a> page.</p>
</div>
</div>
</div>
</section>
<!-- Senior leadership (visible) -->
<section class="py-section-padding bg-lavender-tint/30" id="senior-leadership">
<div class="max-w-container-max mx-auto px-4 sm:px-gutter">
<div class="max-w-4xl mx-auto mb-10 reveal-on-scroll text-center">
<h2 class="font-headline-lg text-headline-lg text-royal-purple mb-3"><span class="section-heading-line">Senior Leadership Team</span></h2>
<p class="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">The team leading our college day to day.</p>
</div>
<div class="max-w-4xl mx-auto reveal-stagger-group">
{"".join(lead_card(m, eager=(i < 2)) for i, m in enumerate(data[0]["members"]))}
</div>
</div>
</section>
<!-- Staff directory accordions -->
<section class="py-section-padding bg-surface-container-lowest" id="staff-directory">
<div class="max-w-container-max mx-auto px-4 sm:px-gutter">
<div class="max-w-4xl mx-auto mb-10 reveal-on-scroll">
<h2 class="font-headline-lg text-headline-lg text-royal-purple mb-3"><span class="section-heading-line">Staff directory</span></h2>
<p class="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">Browse by team. Expand a section to view photos and roles.</p>
</div>
<div class="max-w-4xl mx-auto">
{"".join(sections_html)}
</div>
</div>
</section>
<!-- Related -->
<section class="py-section-padding bg-lavender-tint/30">
<div class="max-w-container-max mx-auto px-4 sm:px-gutter">
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 reveal-stagger-group">
<a class="reveal-stagger-child group flex flex-col p-8 rounded-xl bg-white editorial-shadow hover:bg-royal-purple transition-all duration-300 interactive-hover" href="about-us.html">
<span class="material-symbols-outlined text-royal-purple group-hover:text-on-primary text-3xl mb-4 transition-colors">info</span>
<h3 class="link-card-title text-royal-purple group-hover:text-on-primary mb-2 transition-colors">About us</h3>
<p class="font-body-md text-body-md text-on-surface-variant group-hover:text-on-primary/90 transition-colors">Films, history, and life at Northstowe Secondary College.</p>
</a>
<a class="reveal-stagger-child group flex flex-col p-8 rounded-xl bg-white editorial-shadow hover:bg-royal-purple transition-all duration-300 interactive-hover" href="governance.html">
<span class="material-symbols-outlined text-royal-purple group-hover:text-on-primary text-3xl mb-4 transition-colors">gavel</span>
<h3 class="link-card-title text-royal-purple group-hover:text-on-primary mb-2 transition-colors">Governance</h3>
<p class="font-body-md text-body-md text-on-surface-variant group-hover:text-on-primary/90 transition-colors">Academy Council, trustees, and accountability.</p>
</a>
<a class="reveal-stagger-child group flex flex-col p-8 rounded-xl bg-white editorial-shadow hover:bg-royal-purple transition-all duration-300 interactive-hover" href="ofsted-information.html">
<span class="material-symbols-outlined text-royal-purple group-hover:text-on-primary text-3xl mb-4 transition-colors">verified</span>
<h3 class="link-card-title text-royal-purple group-hover:text-on-primary mb-2 transition-colors">Ofsted</h3>
<p class="font-body-md text-body-md text-on-surface-variant group-hover:text-on-primary/90 transition-colors">Inspection report, ratings, and statutory information.</p>
</a>
</div>
</div>
</section>
<!-- CTA -->
<section class="py-section-padding bg-royal-purple text-center px-4 sm:px-gutter reveal-on-scroll">
<div class="max-w-2xl mx-auto">
<h2 class="font-headline-lg text-headline-lg text-on-primary mb-stack-md">Join our team</h2>
<p class="font-body-lg text-body-lg text-on-primary/90 mb-stack-lg">Interested in working at Northstowe? Explore current vacancies and how to apply.</p>
<a class="bg-on-primary text-deep-plum font-cta-text text-cta-text px-8 py-4 rounded-lg hover:bg-lavender-tint transition-colors inline-flex items-center gap-2 interactive-hover" href="#">
                        Staff vacancies
                        <span class="material-symbols-outlined text-[20px]">work</span>
</a>
</div>
</section>
"""

start_marker = "<!-- Ratings summary -->"
end_marker = "<!-- Trust Partner Section -->"
start = page.find(start_marker)
end = page.find(end_marker)
if start == -1 or end == -1:
    raise SystemExit("Could not find content markers in template")

page = page[:start] + main_block + page[end:]

STAFF_IMG_SCRIPT = """
        function loadDeferredStaffPhotos(root) {
            root.querySelectorAll('img.staff-photo--deferred[data-src]').forEach((img) => {
                const src = img.getAttribute('data-src');
                if (!src || img.getAttribute('src')) return;
                img.src = src;
                img.removeAttribute('data-src');
            });
        }
        document.querySelectorAll('.staff-accordion').forEach((details) => {
            if (details.open) loadDeferredStaffPhotos(details);
            details.addEventListener('toggle', () => {
                if (details.open) loadDeferredStaffPhotos(details);
            });
        });
"""
STAFF_IMG_OLD = re.compile(
    r"\n\s*window\.nscStaffImgFallback[\s\S]*?"
    r"document\.querySelectorAll\('\.staff-accordion'\)\.forEach\([\s\S]*?\}\);\n",
    re.MULTILINE,
)
if STAFF_IMG_OLD.search(page):
    page = STAFF_IMG_OLD.sub("\n" + STAFF_IMG_SCRIPT, page, count=1)
elif "loadDeferredStaffPhotos" not in page:
    page = page.replace(
        "        const heroParallax = document.getElementById('hero-parallax');",
        STAFF_IMG_SCRIPT + "\n        const heroParallax = document.getElementById('hero-parallax');",
        1,
    )

OUT.write_text(page, encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
