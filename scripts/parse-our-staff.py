"""Parse our-staff-source.html into staff-data.json for page generation."""
import html as html_lib
import json
import re
from pathlib import Path


def decode_text(value: str) -> str:
    """Decode WordPress HTML entities (e.g. O&#8217;Sullivan → O'Sullivan)."""
    if not value:
        return value
    text = html_lib.unescape(value)
    if "&#" in text or "&amp;#" in text:
        text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text.replace("\u00a0", " ").replace("&nbsp;", " ")).strip()

SRC = Path(__file__).resolve().parents[1] / ".firecrawl" / "our-staff-source.html"
OUT = Path(__file__).resolve().parents[1] / "about" / "staff-data.json"

text = SRC.read_text(encoding="utf-8")

# Split by accordion sections
section_pattern = re.compile(
    r'<h4 class="advgb-accordion-header-title"[^>]*>\s*(.*?)\s*</h4>',
    re.DOTALL,
)
section_splits = list(section_pattern.finditer(text))
sections = []
for i, m in enumerate(section_splits):
    title = re.sub(r"\s+", " ", m.group(1)).strip()
    title = title.replace("&#8211;", "–").replace("&nbsp;", " ")
    start = m.end()
    if i + 1 < len(section_splits):
        end = section_splits[i + 1].start()
    else:
        end = text.find("</div><!-- .entry-content -->", start)
        if end == -1:
            end = len(text)
    body = text[start:end]
    sections.append({"id": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-"), "title": title, "html": body})

def clean_img_url(block: str) -> str | None:
    # Prefer -scaled derivative when present (required for some Jetpack resize URLs).
    scaled = re.search(
        r'(https://(?:i0\.wp\.com/www\.|www\.)northstowesc\.org/wp-content/uploads/[^\s"?)]+-scaled\.(?:jpe?g|png|webp))',
        block,
        re.I,
    )
    if scaled:
        return scaled.group(1).split("?")[0]
    m = re.search(r'src="(https://www\.northstowesc\.org/wp-content/uploads/[^"]+)"', block)
    if m:
        return m.group(1).split("?")[0]
    m = re.search(r'src="(https://i0\.wp\.com/www\.northstowesc\.org/wp-content/uploads/[^"?]+)', block)
    if m:
        return m.group(1)
    return None

def parse_slt_member(block: str) -> dict | None:
    name_m = re.search(r"<h2[^>]*><strong>([^<]+)</strong>", block)
    if not name_m:
        return None
    name = decode_text(name_m.group(1))
    roles = []
    email = None
    bio = ""
    for p in re.finditer(r'<p class="has-(?:medium|normal|small)-font-size[^"]*">(.*?)</p>', block, re.DOTALL):
        inner = re.sub(r"<br\s*/?>", "\n", p.group(1))
        inner = re.sub(r"<[^>]+>", "", inner).strip()
        inner = decode_text(inner)
        if not inner:
            continue
        if "@" in inner and not email:
            email = inner
        elif not roles and "@" not in inner and len(inner) < 120:
            roles.append(inner)
        elif len(inner) > 40 and not bio:
            bio = inner
    return {
        "name": name,
        "roles": roles,
        "email": email,
        "bio": bio,
        "image": clean_img_url(block),
        "type": "leadership",
    }

def parse_compact_paragraph(block: str) -> dict | None:
    m = re.search(
        r'<p class="has-small-font-size wp-block-paragraph"><strong>([^<]+)</strong>.*?<br[^>]*>(.*?)</p>',
        block,
        re.DOTALL,
    )
    if not m:
        return None
    name = decode_text(m.group(1))
    lines = [
        decode_text(re.sub(r"<[^>]+>", "", ln))
        for ln in re.sub(r"<br\s*/?>", "\n", m.group(2)).split("\n")
    ]
    lines = [ln for ln in lines if ln]
    return {
        "name": name,
        "roles": lines,
        "email": None,
        "bio": "",
        "image": clean_img_url(block),
        "type": "compact",
    }


def parse_compact(block: str) -> dict | None:
    m = re.search(
        r"<strong>([^<]+)</strong>.*?<br[^>]*>(.*?)</p>",
        block,
        re.DOTALL,
    )
    if not m:
        return None
    name = decode_text(m.group(1))
    lines = [
        decode_text(re.sub(r"<[^>]+>", "", ln))
        for ln in re.sub(r"<br\s*/?>", "\n", m.group(2)).split("\n")
    ]
    lines = [ln for ln in lines if ln]
    return {
        "name": name,
        "roles": lines,
        "email": None,
        "bio": "",
        "image": clean_img_url(block),
        "type": "compact",
    }

parsed_sections = []
for sec in sections:
    members = []
    if "Senior Leadership" in sec["title"]:
        parts = re.split(r"<hr[^>]*>", sec["html"])
        for part in parts:
            m = parse_slt_member(part)
            if m:
                members.append(m)
    else:
        seen = set()
        for mt in re.finditer(
            r'<div class="wp-block-media-text[^"]*"[^>]*>.*?</div></div>',
            sec["html"],
            re.DOTALL,
        ):
            block = mt.group(0)
            m = parse_compact(block) or parse_compact_paragraph(block)
            if m and m["name"] not in seen:
                m["name"] = re.sub(r"\s+", " ", m["name"].replace("&nbsp;", " ")).strip()
                seen.add(m["name"])
                members.append(m)
        # fallback: paragraphs only (no photo)
        if not members:
            for p in re.finditer(
                r'<p class="has-small-font-size[^"]*"><strong>([^<]+)</strong>.*?<br[^>]*>(.*?)</p>',
                sec["html"],
                re.DOTALL,
            ):
                name = decode_text(p.group(1))
                lines = [
                    decode_text(re.sub(r"<[^>]+>", "", ln))
                    for ln in re.sub(r"<br\s*/?>", "\n", p.group(2)).split("\n")
                ]
                lines = [ln for ln in lines if ln]
                members.append(
                    {
                        "name": name,
                        "roles": lines,
                        "email": None,
                        "bio": "",
                        "image": None,
                        "type": "compact",
                    }
                )
    parsed_sections.append(
        {"id": sec["id"], "title": sec["title"], "members": members, "count": len(members)}
    )

OUT.write_text(json.dumps(parsed_sections, indent=2), encoding="utf-8")
for s in parsed_sections:
    print(f"{s['title']}: {s['count']}")
print("total", sum(s["count"] for s in parsed_sections))
