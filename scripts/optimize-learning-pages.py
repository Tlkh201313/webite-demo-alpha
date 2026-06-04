"""Speed + polish pass for all learning/**/*.html pages."""
from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEARNING = ROOT / "learning"
CSS_NAME = "learning-content.css"

PRECONNECT = """<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="preconnect" href="https://www.northstowesc.org" crossorigin/>
<link rel="dns-prefetch" href="https://cdn.tailwindcss.com"/>
<link rel="dns-prefetch" href="https://www.northstowesc.org"/>
<link rel="dns-prefetch" href="https://padlet.com"/>"""


def refresh_preconnect(text: str) -> str:
    text = re.sub(
        r'<link rel="preconnect" href="https://i0\.wp\.com"[^>]*>\n?',
        "",
        text,
    )
    if 'preconnect" href="https://www.northstowesc.org"' not in text:
        marker = '<meta content="width=device-width, initial-scale=1.0" name="viewport"/>'
        insert = (
            marker
            + '\n<link rel="preconnect" href="https://www.northstowesc.org" crossorigin/>'
        )
        if marker in text:
            text = text.replace(marker, insert, 1)
    return text


def dedupe_head_hints(text: str) -> str:
    if "<head>" not in text:
        return text
    head_end = text.find("</head>")
    if head_end == -1:
        return text
    head = text[:head_end]
    body = text[head_end:]
    seen: set[str] = set()
    lines: list[str] = []
    for line in head.split("\n"):
        stripped = line.strip()
        if stripped.startswith('<link rel="preconnect"') or stripped.startswith(
            '<link rel="dns-prefetch"'
        ):
            if stripped in seen:
                continue
            seen.add(stripped)
        lines.append(line)
    return "\n".join(lines) + body


def css_href(html_path: Path) -> str:
    rel = Path(
        __import__("os").path.relpath(LEARNING / CSS_NAME, html_path.parent)
    ).as_posix()
    return rel


def ensure_preconnect(text: str) -> str:
    if 'preconnect" href="https://www.northstowesc.org"' in text:
        return text
    marker = '<meta content="width=device-width, initial-scale=1.0" name="viewport"/>'
    insert = marker + "\n" + PRECONNECT
    if marker in text:
        return text.replace(marker, insert, 1)
    return text


def dedupe_stylesheet_links(text: str) -> str:
    """Remove duplicate <link rel="stylesheet"> tags with the same href."""
    seen: set[str] = set()

    def repl(m: re.Match[str]) -> str:
        href = m.group(1)
        if href in seen:
            return ""
        seen.add(href)
        return m.group(0)

    return re.sub(
        r'<link\s+rel=["\']stylesheet["\']\s+href=["\']([^"\']+)["\']\s*/>',
        repl,
        text,
        flags=re.I,
    )


def ensure_stylesheet(text: str, href: str) -> str:
    css_basename = Path(href).name
    link = f'<link rel="stylesheet" href="{href}"/>'
    if css_basename in text:
        existing = re.search(
            rf'<link rel="stylesheet" href="([^"]*{re.escape(css_basename)})"/>',
            text,
        )
        if existing and existing.group(1) == href:
            text = dedupe_stylesheet_links(text)
            return text
        text = re.sub(
            rf'<link rel="stylesheet" href="[^"]*{re.escape(css_basename)}"/>',
            link,
            text,
            count=1,
        )
        return dedupe_stylesheet_links(text)
    anchor = PRECONNECT.split("\n")[-1] + "\n"
    if anchor.strip() in text:
        text = text.replace(anchor, anchor + link + "\n", 1)
    else:
        text = text.replace(
            '<meta name="referrer" content="strict-origin-when-cross-origin"/>',
            f'<meta name="referrer" content="strict-origin-when-cross-origin"/>\n{link}',
            1,
        )
    return dedupe_stylesheet_links(text)


def fix_broken_css(text: str) -> str:
    return re.sub(
        r"\.entry-content\s+\n\s+\.padlet-embed",
        ".entry-content .padlet-embed",
        text,
    )


def _strip_jetpack_cdn_url(url: str) -> str:
    url = html_lib.unescape(url)
    url = re.sub(
        r"https://i0\.wp\.com/www\.northstowesc\.org(/wp-content/uploads/[^?\s\"']+)",
        r"https://www.northstowesc.org\1",
        url,
    )
    url = re.sub(
        r"https://i0\.wp\.com/padlet\.net(/[^?\s\"']+)",
        r"https://padlet.net\1",
        url,
    )
    url = re.sub(
        r"(https://(?:www\.)?northstowesc\.org/wp-content/uploads/[^?\s\"']+)\?[^\"'\s]*",
        r"\1",
        url,
    )
    url = re.sub(
        r"(https://padlet\.net/[^?\s\"']+)\?[^\"'\s]*",
        r"\1",
        url,
    )
    return url


def fix_wp_image_urls(text: str) -> str:
    # Wrong PDF preview filename scraped from live WP (404 on origin + expired Jetpack CDN)
    text = text.replace("Year-8-pathway-2026-2-pdf", "Year-8-pathway-2026-pdf")

    def fix_attr(match: re.Match[str]) -> str:
        attr, val = match.group(1), match.group(2)
        if "i0.wp.com" not in val:
            return match.group(0)
        if attr == "srcset":
            parts = []
            for part in val.split(","):
                part = part.strip()
                if not part:
                    continue
                bits = part.rsplit(" ", 1)
                if len(bits) == 2:
                    parts.append(f"{_strip_jetpack_cdn_url(bits[0].strip())} {bits[1]}")
                else:
                    parts.append(_strip_jetpack_cdn_url(part))
            return f'{attr}="{", ".join(parts)}"'
        return f'{attr}="{_strip_jetpack_cdn_url(val)}"'

    text = re.sub(r'(src|srcset)="([^"]*)"', fix_attr, text)
    text = re.sub(
        r"https://i0\.wp\.com/([^/\"'\s]+)(/[^\"'\s]*?)(?:\?[^\"'\s]*)?",
        r"https://\1\2",
        text,
    )
    return text


def split_entry_content(text: str) -> tuple[str | None, str, str]:
    for marker in (
        '<div class="entry-content learning-stagger">',
        '<div class="entry-content">',
    ):
        parts = text.split(marker, 1)
        if len(parts) == 2:
            return marker, parts[0], parts[1]
    return None, text, ""


def join_entry_content(marker: str, before: str, body: str, closing: str, after: str) -> str:
    return before + marker + body + closing + after


def strip_entry_noscript(text: str) -> str:
    if "<noscript>" not in text:
        return text
    marker, before, rest = split_entry_content(text)
    if not marker:
        return text
    end = re.search(r"(.*)(</div>\s*</article>)", rest, re.S)
    if not end:
        return text
    body = re.sub(r"<noscript>.*?</noscript>", "", end.group(1), flags=re.S)
    return before + marker + body + end.group(2) + rest[end.end() :]


def lazy_load_media(text: str) -> str:
    # Padlet embeds — defer until near viewport
    text = re.sub(
        r'<iframe(?![^>]*\bloading=)(?=[^>]*src="https://padlet\.com/)',
        '<iframe loading="lazy"',
        text,
    )
    text = text.replace('<iframe loading="lazy" <iframe', '<iframe loading="lazy"')
    text = re.sub(
        r'(<iframe\b)\s+loading="lazy"\s+loading="lazy"',
        r'\1 loading="lazy"',
        text,
    )

    # Videos default to metadata only
    def fix_video(m: re.Match[str]) -> str:
        tag = m.group(0)
        if re.search(r"\bpreload=", tag, re.I):
            return tag
        return tag.replace("<video", '<video preload="metadata"', 1)

    text = re.sub(r"<video\b[^>]*>", fix_video, text, flags=re.I)

    marker, before, rest = split_entry_content(text)
    if not marker:
        return text
    end = re.search(r"(.*)(</div>\s*</article>)", rest, re.S)
    if not end:
        return text
    body, closing = end.group(1), end.group(2)
    after = rest[end.end() :]
    img_count = 0

    def fix_img(m: re.Match[str]) -> str:
        nonlocal img_count
        tag = m.group(0)
        img_count += 1
        if img_count == 1 and not re.search(r'\bloading="', tag, re.I):
            if 'decoding="async"' not in tag:
                tag = tag.replace("<img", '<img decoding="async"', 1)
            return tag
        if not re.search(r'\bloading="', tag, re.I):
            tag = tag.replace("<img", '<img loading="lazy"', 1)
        if 'decoding="async"' not in tag:
            tag = tag.replace("<img", '<img decoding="async"', 1)
        return tag

    body = re.sub(r"<img\b[^>]*>", fix_img, body, flags=re.I)
    body = re.sub(
        r'<iframe(?![^>]*\bloading=)(?=[^>]*\bsrc=")',
        '<iframe loading="lazy"',
        body,
    )
    return before + marker + body + closing + after


def lazy_trust_logos(text: str) -> str:
    if 'border-outline-variant reveal-on-scroll">' not in text:
        return text
    return re.sub(
        r'(<section class="py-section-padding border-t border-outline-variant reveal-on-scroll">.*?<img)(?![^>]*\bloading=)',
        r'\1 loading="lazy" decoding="async"',
        text,
        count=1,
        flags=re.S,
    )


REVEAL_QUERY = (
    ".reveal-on-scroll, .reveal-from-left, .reveal-from-right, "
    ".reveal-scale, .value-card, .learning-split-reveal"
)
REVEAL_QUERY_LEGACY = (
    ".reveal-on-scroll, .reveal-from-left, .reveal-from-right, "
    ".reveal-scale, .value-card, .learning-split-reveal, .learning-reveal"
)
REVEAL_QUERY_OLD = (
    ".reveal-on-scroll, .reveal-from-left, .reveal-from-right, "
    ".reveal-scale, .value-card"
)


def apply_learning_motion_markup(text: str) -> str:
    text = text.replace(
        'class="nsc-page-with-sidebar reveal-on-scroll"',
        'class="nsc-page-with-sidebar learning-split-reveal"',
    )
    text = text.replace(
        '<header class="entry-header learning-reveal">',
        '<header class="entry-header">',
    )
    if 'class="entry-content learning-stagger"' not in text:
        text = text.replace(
            '<div class="entry-content">',
            '<div class="entry-content learning-stagger">',
            1,
        )
    return text


REVEAL_FLUSH_MARKER = "flushRevealVisibility"

REVEAL_FLUSH_BLOCK = """
        const flushRevealVisibility = () => {
            document.querySelectorAll(
                '.reveal-on-scroll, .reveal-from-left, .reveal-from-right, .reveal-scale, .value-card, .learning-split-reveal, .reveal-stagger-group, .learning-stagger'
            ).forEach((el) => {
                if (el.classList.contains('is-visible')) return;
                const rect = el.getBoundingClientRect();
                const vh = window.innerHeight || document.documentElement.clientHeight;
                if (rect.bottom > 0 && rect.top < vh) {
                    el.classList.add('is-visible');
                }
            });
            document.querySelectorAll('.entry-content img[loading="lazy"]').forEach((img) => {
                const rect = img.getBoundingClientRect();
                const vh = window.innerHeight || document.documentElement.clientHeight;
                if (rect.bottom > 0 && rect.top < vh && !img.complete) {
                    img.loading = 'eager';
                }
            });
        };
        flushRevealVisibility();
        requestAnimationFrame(flushRevealVisibility);
        window.addEventListener('pageshow', () => {
            document.querySelectorAll(
                '.reveal-on-scroll, .reveal-from-left, .reveal-from-right, .reveal-scale, .value-card, .learning-split-reveal, .reveal-stagger-group, .learning-stagger'
            ).forEach((el) => el.classList.add('is-visible'));
        });
        setTimeout(() => {
            document.querySelectorAll(
                '.reveal-on-scroll, .reveal-from-left, .reveal-from-right, .reveal-scale, .value-card, .learning-split-reveal, .reveal-stagger-group, .learning-stagger'
            ).forEach((el) => el.classList.add('is-visible'));
        }, 1200);
"""

REDUCED_MOTION_OLD = """                    if (!prefersReducedMotion) {
                        entry.target.classList.add('is-visible');
                    } else {
                        // Immediately make visible without transition if motion is reduced
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'none';
                        entry.target.style.transition = 'none';
                    }"""

REDUCED_MOTION_NEW = """                    entry.target.classList.add('is-visible');
                    if (prefersReducedMotion) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'none';
                        entry.target.style.transition = 'none';
                    }"""


def harden_reveal_script(text: str) -> str:
    if REDUCED_MOTION_OLD in text:
        text = text.replace(REDUCED_MOTION_OLD, REDUCED_MOTION_NEW, 1)
    text = text.replace("threshold: 0.15", "threshold: 0.01", 1)
    if (
        "const observerOptions = {" in text
        and "rootMargin: '40px 0px 40px 0px'" not in text
    ):
        text = text.replace(
            "const observerOptions = {\n            root: null,\n            rootMargin: '0px',",
            "const observerOptions = {\n            root: null,\n            rootMargin: '40px 0px 40px 0px',",
            1,
        )
    if REVEAL_FLUSH_MARKER in text:
        return text
    for anchor in (
        "        document.querySelectorAll('.reveal-stagger-group, .learning-stagger').forEach((group) => staggerObserver.observe(group));",
        "        document.querySelectorAll('.reveal-stagger-group').forEach((group) => staggerObserver.observe(group));",
    ):
        if anchor in text:
            text = text.replace(anchor, anchor + REVEAL_FLUSH_BLOCK, 1)
            break
    return text


def extend_reveal_observer(text: str) -> str:
    if ", .learning-reveal" in text:
        text = text.replace(
            ", .learning-split-reveal, .learning-reveal",
            ", .learning-split-reveal",
        )
    if REVEAL_QUERY not in text:
        for legacy in (REVEAL_QUERY_LEGACY, REVEAL_QUERY_OLD):
            if legacy in text:
                text = text.replace(f"'{legacy}'", f"'{REVEAL_QUERY}'", 1)
                text = text.replace(f'"{legacy}"', f'"{REVEAL_QUERY}"', 1)
                break
    if "'.reveal-stagger-group, .learning-stagger'" not in text:
        text = text.replace(
            "document.querySelectorAll('.reveal-stagger-group')",
            "document.querySelectorAll('.reveal-stagger-group, .learning-stagger')",
            1,
        )
    return text


def optimize_banner_img(text: str) -> str:
    def fix_banner(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "fetchpriority=" not in tag:
            tag = tag.replace("<img", '<img fetchpriority="high"', 1)
        if 'decoding="async"' not in tag:
            tag = tag.replace("<img", '<img decoding="async"', 1)
        tag = re.sub(r'\sloading="lazy"', "", tag)
        return tag

    return re.sub(
        r'<img alt="" class="nsc-inner-banner__img"[^>]*>',
        fix_banner,
        text,
        count=1,
    )


def patch_file(path: Path, css_base: Path | None = None) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original
    href = css_href(path) if css_base is None else Path(
        __import__("os").path.relpath(css_base, path.parent)
    ).as_posix()
    text = ensure_preconnect(text)
    text = refresh_preconnect(text)
    text = dedupe_head_hints(text)
    text = ensure_stylesheet(text, href)
    text = fix_broken_css(text)
    text = fix_wp_image_urls(text)
    text = strip_entry_noscript(text)
    text = lazy_load_media(text)
    text = lazy_trust_logos(text)
    text = optimize_banner_img(text)
    text = apply_learning_motion_markup(text)
    text = extend_reveal_observer(text)
    text = harden_reveal_script(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for fp in sorted(LEARNING.rglob("*.html")):
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"optimized {changed} file(s)")


if __name__ == "__main__":
    main()
