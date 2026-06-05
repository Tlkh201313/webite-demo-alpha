"""Build client-side search index from static HTML pages."""
from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "site-search-index.json"

SKIP_DIRS = {
    ".git",
    ".github",
    "mobile-app",
    "graphify-out",
    ".firecrawl",
    "docs",
    "scripts",
    "node_modules",
}

SKIP_FILES = {"search.html", "index.html"}


def strip_tags(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def first_match(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.I | re.S)
    return strip_tags(match.group(1)) if match else ""


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return rel


def extract_entry(path: Path) -> dict | None:
    html = path.read_text(encoding="utf-8", errors="replace")
    title = first_match(r"<title>(.*?)</title>", html)
    h1 = first_match(r"<h1[^>]*>(.*?)</h1>", html)
    desc = first_match(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html)
    if not desc:
        desc = first_match(r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', html)

    content_match = re.search(
        r'class="entry-content[^"]*"(.*?</(?:main|article|div)>)',
        html,
        re.I | re.S,
    )
    body = strip_tags(content_match.group(1))[:500] if content_match else ""
    if not body:
        body = strip_tags(html)[:400]

    label = h1 or title or path.stem.replace("-", " ").title()
    if not label:
        return None

    keywords: list[str] = []
    for nav_match in re.finditer(r'class="nav-trigger[^"]*"[^>]*>([^<]+)', html):
        kw = strip_tags(nav_match.group(1)).replace("expand_more", "").strip()
        if kw and kw not in keywords:
            keywords.append(kw)

    return {
        "title": title or label,
        "label": label,
        "url": page_url(path),
        "section": path.parent.name.replace("-", " ").title() if path.parent != ROOT else "Home",
        "description": desc or body[:160],
        "text": " ".join(filter(None, [title, h1, desc, body, " ".join(keywords)])),
    }


def staff_entries() -> list[dict]:
    staff_json = ROOT / "about" / "staff-data.json"
    if not staff_json.is_file():
        return []
    data = json.loads(staff_json.read_text(encoding="utf-8"))
    entries: list[dict] = []
    sections = data if isinstance(data, list) else data.get("staff", [])
    for section in sections:
        if not isinstance(section, dict):
            continue
        for person in section.get("members", []):
            name = person.get("name", "").strip()
            roles = person.get("roles") or []
            role = ", ".join(roles) if isinstance(roles, list) else str(roles)
            if not name:
                continue
            entries.append(
                {
                    "title": name,
                    "label": name,
                    "url": "about/our-staff.html",
                    "section": "Staff",
                    "description": role or "Northstowe Secondary College staff member",
                    "text": f"{name} {role} staff our staff",
                }
            )
    return entries


def main() -> None:
    entries: list[dict] = []
    seen_urls: set[str] = set()

    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        entry = extract_entry(path)
        if not entry or entry["url"] in seen_urls:
            continue
        seen_urls.add(entry["url"])
        entries.append(entry)

    for entry in staff_entries():
        key = f"staff:{entry['title']}"
        if key in seen_urls:
            continue
        seen_urls.add(key)
        entries.append(entry)

    entries.sort(key=lambda item: (item["section"].lower(), item["label"].lower()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
