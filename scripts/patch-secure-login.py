"""Replace header Secure Login button with working dropdown + wire assets."""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_FILE = ROOT / "nsc-secure-login.css"
JS_FILE = ROOT / "nsc-secure-login.js"

OLD_BUTTON_RE = re.compile(
    r'<button class="bg-white text-royal-purple[^"]*">\s*Secure Login\s*</button>',
    re.IGNORECASE | re.DOTALL,
)

CSS_LINK = '<link rel="stylesheet" href="{href}"/>'
JS_SCRIPT = '<script src="{href}" defer></script>'

EXTERNAL_LINKS: list[tuple[str, list[tuple[str, str, str, str | None]]]] = [
    (
        "Parents &amp; carers",
        [
            (
                "MCAS (Parent login)",
                "https://www.mychildatschool.com/MCAS/MCSParentLogin",
                "family_restroom",
                "Payments, messages and student information",
            ),
        ],
    ),
    (
        "School systems",
        [
            ("Microsoft 365", "https://cmat.cloud", "cloud", None),
            ("School email", "https://outlook.office.com", "mail", None),
            (
                "Oliver library",
                "https://northstowe.oliverasp.co.uk/library/home/news",
                "local_library",
                None,
            ),
        ],
    ),
    (
        "Learning platforms",
        [
            (
                "Languagenut",
                "https://www.languagenut.com/resources/en-gb/index.html#/LoginScreen?packages=8,34,43,54,33,66&product=languagenut&conditions=1",
                "translate",
                None,
            ),
            ("Seneca Learning", "https://app.senecalearning.com/login", "school", None),
            (
                "SmartRevise",
                "https://smartrevise.online/Account/Login",
                "auto_stories",
                None,
            ),
            (
                "Sparx Maths",
                "https://auth.sparxmaths.uk/oauth2/auth?client_id=sparx-maths-sw&hd=7945fbe6-d4b2-4b01-89b0-207a949b4642&redirect_uri=https%3A%2F%2Fstudentapi.api.sparxmaths.uk%2Foauth%2Fcallback&response_type=code&scope=openid+profile+email&state=oQnSYpp33PJrbUHBBLHSRmHng-XLHEJxwnL0NaaE9s9a49odEHNP8MAhnWX3Jcvw6CcrWJhwfkITJzBAV7vJedkZeJ2649ueXcEP3J-essYFyP4sS6OV-E5vRhMCpN6Wnfhk237OPGJk3C9Td1EapOzlzkO7RL7rriaKfnFwTYgWWxE7rlI3cIEkSuRH_CM0jg5CMTsLyT7mbdYezZRRWPH8g9htzXObsrs52Gay6K9sZJrPhjp4YL2KAhL-pWuc24tzU7H09vn8L1Xk",
                "calculate",
                None,
            ),
            (
                "Sparx Reader",
                "https://auth.sparxmaths.uk/oauth2/auth?client_id=sparx-reader&hd=7945fbe6-d4b2-4b01-89b0-207a949b4642&redirect_uri=https%3A%2F%2Fapi.sparxreader.com%2Foauth2%2Fcallback%2Fsparx&response_type=code&scope=openid+profile+email&state=q24C5E4qk-5tT3-6ITzxd1UsPjOptePH1w6tLfyelrmoUTkrOAg0yyEf4Oxn2Jou8h9x8Aax9YcfswqCjmoh1L-Su7Dzb9BO_llnfCWYWwRD42L_4yNWznCWIChy8l2tA9q6vuRzF72Fbzzhxy7HoGFNzKRj82DIYjA_do4IPgB1P6ff0ydsm1IJpIFmhwJqHnKrI2pL6eguka7FWAlh4dke2pw0JQ%3D%3D",
                "menu_book",
                None,
            ),
            (
                "Tassomai",
                "https://app.tassomai.com/login?returnUrl=%2Fdashboard",
                "quiz",
                None,
            ),
        ],
    ),
]


def rel_href(html_path: Path, asset: Path) -> str:
    return Path(os.path.relpath(asset, html_path.parent)).as_posix()


def bromcom_guide_href(html_path: Path) -> str:
    target = ROOT / "parents-and-carers" / "bromcom.html"
    return Path(os.path.relpath(target, html_path.parent)).as_posix()


def render_link(
    label: str,
    href: str,
    icon: str,
    hint: str | None,
    *,
    local: bool = False,
) -> str:
    hint_html = ""
    if hint:
        hint_html = f'<span class="nsc-secure-login__link-hint">{hint}</span>'
    local_class = " nsc-secure-login__link--local" if local else ""
    target = "" if local else ' target="_blank" rel="noopener noreferrer"'
    return f"""<li>
<a class="nsc-secure-login__link{local_class}" href="{href}" role="menuitem"{target}>
<span class="nsc-secure-login__link-icon" aria-hidden="true"><span class="material-symbols-outlined">{icon}</span></span>
<span class="nsc-secure-login__link-text">
<span class="nsc-secure-login__link-label">{label}</span>
{hint_html}
</span>
</a>
</li>"""


def secure_login_html(html_path: Path) -> str:
    groups: list[str] = []
    for title, links in EXTERNAL_LINKS:
        items = []
        for label, url, icon, hint in links:
            items.append(render_link(label, url, icon, hint))
        if title == "Parents &amp; carers":
            items.append(
                render_link(
                    "Bromcom / MCAS guide",
                    bromcom_guide_href(html_path),
                    "help",
                    "Setup help on our website",
                    local=True,
                )
            )
        groups.append(
            f"""<div class="nsc-secure-login__group">
<p class="nsc-secure-login__group-title">{title}</p>
<ul class="nsc-secure-login__list" role="none">{"".join(items)}</ul>
</div>"""
        )

    return f"""<div class="nsc-secure-login" data-nsc-secure-login>
<button type="button" class="nsc-secure-login__trigger" aria-expanded="false" aria-haspopup="true" aria-controls="nsc-secure-login-panel" id="nsc-secure-login-trigger">
<span class="material-symbols-outlined" aria-hidden="true">lock</span>
<span class="nsc-secure-login__label">Secure login</span>
<span class="material-symbols-outlined nsc-secure-login__chevron" aria-hidden="true">expand_more</span>
</button>
<div class="nsc-secure-login__panel" id="nsc-secure-login-panel" role="menu" aria-labelledby="nsc-secure-login-trigger" hidden>
<p class="nsc-secure-login__intro">Choose a platform to sign in. External links open in a new tab.</p>
{"".join(groups)}
</div>
</div>"""


def ensure_css_link(text: str, href: str) -> str:
    marker = f'href="{href}"'
    if marker in text:
        return text
    link = CSS_LINK.format(href=href)
    skel = re.search(r'(<link rel="stylesheet" href="[^"]*nsc-skeleton\.css"/>)', text)
    if skel:
        return text.replace(skel.group(1), skel.group(1) + "\n" + link, 1)
    chrome = re.search(r'(<link rel="stylesheet" href="[^"]*site-chrome\.css"/>)', text)
    if chrome:
        return text.replace(chrome.group(1), chrome.group(1) + "\n" + link, 1)
    if "</head>" in text:
        return text.replace("</head>", link + "\n</head>", 1)
    return text


def ensure_js_script(text: str, href: str) -> str:
    marker = f'src="{href}"'
    if marker in text:
        return text
    script = JS_SCRIPT.format(href=href)
    skel_js = re.search(r'(<script src="[^"]*nsc-skeleton\.js"></script>)', text)
    if skel_js:
        return text.replace(skel_js.group(1), skel_js.group(1) + "\n" + script, 1)
    if "</body>" in text:
        return text.replace("</body>", script + "\n</body>", 1)
    return text


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    if OLD_BUTTON_RE.search(text):
        text = OLD_BUTTON_RE.sub(secure_login_html(path), text, count=1)
    elif 'data-nsc-secure-login' in text and "nsc-secure-login__panel" in text:
        text = re.sub(
            r'<div class="nsc-secure-login" data-nsc-secure-login>.*?</div>\s*</div>\s*(?=</div>\s*<!-- Navigation)',
            secure_login_html(path) + "\n",
            text,
            count=1,
            flags=re.DOTALL,
        )

    css_href = rel_href(path, CSS_FILE)
    js_href = rel_href(path, JS_FILE)
    text = ensure_css_link(text, css_href)
    text = ensure_js_script(text, js_href)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


SKIP_HTML = {ROOT / "index.html"}


def main() -> None:
    changed = 0
    for fp in sorted(ROOT.rglob("*.html")):
        if "node_modules" in fp.parts or ".firecrawl" in fp.parts or "graphify-out" in fp.parts:
            continue
        if fp.parent == ROOT / "scripts" or fp in SKIP_HTML:
            continue
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"Patched {changed} HTML file(s) with secure login dropdown")


if __name__ == "__main__":
    main()
