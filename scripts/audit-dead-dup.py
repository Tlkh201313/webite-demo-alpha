"""
Scan nsc-web for dead files, unreferenced scripts, and duplicate patterns.
Read-only by default. Use --apply-safe to remove high-confidence orphans.

  python scripts/audit-dead-dup.py
  python scripts/audit-dead-dup.py --apply-safe
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPORT_MD = DOCS / "dead-dup-scan.md"
REPORT_JSON = DOCS / "dead-dup-scan.json"

CONVENTIONS = ROOT / ".cursor" / "rules" / "nsc-web-conventions.mdc"
FIRECRAWL = ROOT / ".firecrawl"
SCRIPTS = ROOT / "scripts"

KEEP_FIRECRAWL = {
    "contact-us-source.html",
    "our-staff-source.html",
    "pandesports-northstowe.html",
}

SAFE_DELETE_FILES = [
    ROOT / "test.html",
    SCRIPTS / "apply-contact-design.py",
]

HREF_HTML = re.compile(
    r'href=["\'](?!https?://|mailto:|tel:|#)([^"\']+\.html(?:#[^"\']*)?)["\']',
    re.I,
)
STYLESHEET_LINK = re.compile(
    r'<link\s+rel=["\']stylesheet["\']\s+href=["\']([^"\']+)["\']\s*/>',
    re.I,
)
MAP_SECTION = re.compile(
    r"<section\s+class=[\"']nsc-map-section[\"'].*?</section>",
    re.S | re.I,
)

DEFERRED_DUPES = """## Documented duplicates (deferred)

1. **Inline chrome CSS** — ~90 HTML files duplicate nav/motion `<style>` blocks; extract to `site-chrome.css`.
2. **Map section** — `main.html` and `contact-us.html` duplicate `nsc-map-section`; regen from `patch-hire-contact-nav.map_section_html()`.
3. **Section builders** — `build-parents-pages.py` / `build-news-pages.py` parallel `build-learning-pages.py`.
4. **Section CSS forks** — `parents-content.css` / `news-content.css` forked from `learning-content.css`.
5. **Placeholder images** — replace `googleusercontent.com/aida` with `wp-content` URLs sitewide.
6. **contact-us.html** — verify News nav uses root-relative `news-and-events/` not `../news-and-events/` from repo root.
"""


def _norm_path(href: str, from_file: Path) -> str | None:
    href = href.split("#")[0].strip()
    if not href or href.startswith(("http://", "https://", "mailto:", "tel:")):
        return None
    try:
        target = (from_file.parent / href).resolve()
        if target.suffix.lower() != ".html":
            return None
        return target.relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return None


def scan_orphan_html() -> dict:
    html_files = [
        p
        for p in ROOT.rglob("*.html")
        if ".firecrawl" not in p.parts
        and "node_modules" not in p.parts
        and "scripts" not in p.parts
    ]
    inbound: dict[str, int] = {p.relative_to(ROOT).as_posix(): 0 for p in html_files}
    broken_refs: list[dict] = []

    for fp in html_files:
        text = fp.read_text(encoding="utf-8", errors="replace")
        for m in HREF_HTML.finditer(text):
            rel = _norm_path(m.group(1), fp)
            if rel is None:
                continue
            target = ROOT / rel
            if target.exists():
                inbound[rel] = inbound.get(rel, 0) + 1
            else:
                broken_refs.append(
                    {"from": fp.relative_to(ROOT).as_posix(), "href": m.group(1)}
                )

    entry_points = {"main.html", "welcome.html", "contact-us.html"}
    orphans = [
        path
        for path, count in sorted(inbound.items())
        if count == 0 and path not in entry_points
    ]
    return {
        "html_count": len(html_files),
        "orphans": orphans,
        "broken_refs": broken_refs[:50],
        "broken_ref_count": len(broken_refs),
    }


def scan_scripts() -> dict:
    py_files = sorted(SCRIPTS.glob("*.py"))
    conventions_text = (
        CONVENTIONS.read_text(encoding="utf-8") if CONVENTIONS.exists() else ""
    )
    all_text_parts: list[str] = [conventions_text]
    for p in ROOT.rglob("*"):
        if p.suffix in {".py", ".md", ".mdc", ".ps1"} and p != Path(__file__):
            if ".firecrawl" in p.parts:
                continue
            try:
                all_text_parts.append(p.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                pass
    corpus = "\n".join(all_text_parts)

    documented = set(re.findall(r"scripts/([\w-]+\.py)", conventions_text))
    documented.add("audit-dead-dup.py")

    unreferenced: list[str] = []
    referenced_not_doc: list[str] = []
    for fp in py_files:
        name = fp.name
        if name == "audit-dead-dup.py":
            continue
        # Count references excluding the file itself
        pattern = re.compile(rf"\b{re.escape(name)}\b")
        hits = 0
        for part in all_text_parts:
            if pattern.search(part):
                hits += 1
        self_only = fp.read_text(encoding="utf-8", errors="replace")
        if hits <= 1 and "if __name__" in self_only:
            unreferenced.append(name)
        elif name not in documented and hits > 1:
            referenced_not_doc.append(name)

    return {
        "script_count": len(py_files),
        "documented_in_conventions": sorted(documented),
        "unreferenced_one_shots": sorted(unreferenced),
        "referenced_not_in_conventions": sorted(referenced_not_doc),
    }


def scan_firecrawl() -> dict:
    if not FIRECRAWL.exists():
        return {"exists": False, "unused": [], "keep": list(KEEP_FIRECRAWL), "safe_delete": []}

    used_in_py = set()
    for py in SCRIPTS.glob("*.py"):
        text = py.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'\.firecrawl\s*/\s*["\']([^"\']+)["\']', text):
            used_in_py.add(m.group(1))
        for m in re.finditer(r'FIRECRAWL\s*/\s*["\']([^"\']+)["\']', text):
            used_in_py.add(m.group(1))

    all_files = sorted(FIRECRAWL.iterdir())
    unused: list[str] = []
    keep: list[str] = []
    for fp in all_files:
        if fp.is_dir():
            continue
        name = fp.name
        if name in KEEP_FIRECRAWL or name in used_in_py:
            keep.append(name)
        else:
            unused.append(name)

    return {
        "exists": True,
        "total": len([f for f in all_files if f.is_file()]),
        "used_in_scripts": sorted(used_in_py),
        "keep": sorted(keep),
        "unused": sorted(unused),
        "safe_delete": sorted(
            n
            for n in unused
            if n.endswith("-source.html")
            or n == "newsletter-feed.xml"
            or n.startswith("xnxox")
        ),
    }


def scan_dup_stylesheets() -> dict:
    dupes: list[dict] = []
    for fp in ROOT.rglob("*.html"):
        if ".firecrawl" in fp.parts:
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        counts: dict[str, int] = {}
        for m in STYLESHEET_LINK.finditer(text):
            href = m.group(1)
            if "content.css" in href or href.endswith("site-content.css"):
                counts[href] = counts.get(href, 0) + 1
        for href, n in counts.items():
            if n > 1:
                dupes.append(
                    {
                        "file": fp.relative_to(ROOT).as_posix(),
                        "href": href,
                        "count": n,
                    }
                )
    return {"duplicate_stylesheet_links": dupes, "files_affected": len(dupes)}


def _normalize_map_block(block: str) -> str:
    block = re.sub(r"\s+", " ", block.strip())
    block = block.replace("&amp;", "&")
    return block


def scan_map_drift() -> dict:
    main = ROOT / "main.html"
    contact = ROOT / "contact-us.html"
    result: dict = {"main_has_map": False, "contact_has_map": False, "drift": []}
    if not main.exists() or not contact.exists():
        return result

    main_text = main.read_text(encoding="utf-8", errors="replace")
    contact_text = contact.read_text(encoding="utf-8", errors="replace")
    main_m = MAP_SECTION.search(main_text)
    contact_m = MAP_SECTION.search(contact_text)
    result["main_has_map"] = bool(main_m)
    result["contact_has_map"] = bool(contact_m)
    if main_m and contact_m:
        mn = _normalize_map_block(main_m.group(0))
        cn = _normalize_map_block(contact_m.group(0))
        if mn != cn:
            result["drift"].append("main.html vs contact-us.html (normalized whitespace/entities differ)")
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "patch_hire", SCRIPTS / "patch-hire-contact-nav.py"
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        canonical = _normalize_map_block(mod.map_section_html())
        if main_m and _normalize_map_block(main_m.group(0)) != canonical:
            result["drift"].append("main.html vs patch-hire-contact-nav.map_section_html()")
        if contact_m and _normalize_map_block(contact_m.group(0)) != canonical:
            result["drift"].append("contact-us.html vs patch-hire-contact-nav.map_section_html()")
    except Exception as exc:
        result["drift"].append(f"could not load map_section_html: {exc}")
    return result


def scan_placeholder_images() -> dict:
    aida_files: list[dict] = []
    wp_files: list[str] = []
    for fp in ROOT.rglob("*.html"):
        if ".firecrawl" in fp.parts:
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        aida = len(re.findall(r"googleusercontent\.com/aida", text, re.I))
        wp = len(re.findall(r"northstowesc\.org/wp-content", text, re.I))
        if aida:
            aida_files.append(
                {"file": fp.relative_to(ROOT).as_posix(), "aida_count": aida, "wp_count": wp}
            )
        if wp and aida == 0:
            wp_files.append(fp.relative_to(ROOT).as_posix())
    aida_files.sort(key=lambda x: -x["aida_count"])
    return {
        "files_with_aida": len(aida_files),
        "top_aida": aida_files[:15],
        "files_wp_only_sample": wp_files[:10],
    }


def scan_content_fragments() -> dict:
    contact_content = SCRIPTS / "contact-page-content.html"
    refs = []
    for py in SCRIPTS.glob("*.py"):
        if py.name == "audit-dead-dup.py":
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        if "contact-page-content.html" in text:
            refs.append(py.name)
    h = ""
    if contact_content.exists():
        h = hashlib.sha256(contact_content.read_bytes()).hexdigest()[:12]
    return {
        "contact_page_content_sha256_12": h,
        "scripts_referencing_fragment": sorted(refs),
    }


def build_report(data: dict) -> str:
    lines = [
        "# Dead and duplicate code scan",
        "",
        f"Generated by `scripts/audit-dead-dup.py` from `{ROOT}`.",
        "",
        "## Summary",
        "",
        f"- HTML pages scanned: **{data['orphan_html']['html_count']}**",
        f"- Orphan HTML (no inbound links): **{len(data['orphan_html']['orphans'])}**",
        f"- Broken relative HTML hrefs: **{data['orphan_html']['broken_ref_count']}**",
        f"- Unreferenced one-shot scripts: **{len(data['scripts']['unreferenced_one_shots'])}**",
        f"- Unused `.firecrawl` files: **{len(data['firecrawl'].get('unused', []))}**",
        f"- Duplicate section stylesheet links: **{data['dup_stylesheets']['files_affected']}** files",
        f"- Pages with Google `aida` placeholders: **{data['placeholders']['files_with_aida']}**",
        "",
        "## Orphan HTML",
        "",
    ]
    if data["orphan_html"]["orphans"]:
        for o in data["orphan_html"]["orphans"]:
            lines.append(f"- `{o}`")
    else:
        lines.append("- _(none)_")
    lines.extend(["", "## Unreferenced scripts (one-shots)", ""])
    for s in data["scripts"]["unreferenced_one_shots"]:
        lines.append(f"- `scripts/{s}`")
    lines.extend(["", "## `.firecrawl` — safe to delete", ""])
    for n in data["firecrawl"].get("safe_delete", []):
        lines.append(f"- `.firecrawl/{n}`")
    lines.extend(["", "## `.firecrawl` — keep", ""])
    for n in data["firecrawl"].get("keep", []):
        lines.append(f"- `.firecrawl/{n}`")
    lines.extend(["", "## Duplicate stylesheet links", ""])
    for d in data["dup_stylesheets"]["duplicate_stylesheet_links"][:30]:
        lines.append(f"- `{d['file']}`: `{d['href']}` × {d['count']}")
    if len(data["dup_stylesheets"]["duplicate_stylesheet_links"]) > 30:
        lines.append(f"- _…and {len(data['dup_stylesheets']['duplicate_stylesheet_links']) - 30} more_")
    lines.extend(["", "## Map section drift", ""])
    if data["map_drift"]["drift"]:
        for d in data["map_drift"]["drift"]:
            lines.append(f"- {d}")
    else:
        lines.append("- _(none after normalization)_")
    lines.extend(["", "## Placeholder images (top by aida count)", ""])
    for item in data["placeholders"]["top_aida"]:
        lines.append(f"- `{item['file']}`: {item['aida_count']} aida, {item['wp_count']} wp-content")
    lines.extend(["", DEFERRED_DUPES, ""])
    return "\n".join(lines) + "\n"


def apply_safe_deletes(firecrawl: dict) -> list[str]:
    deleted: list[str] = []
    for path in SAFE_DELETE_FILES:
        if path.exists():
            path.unlink()
            deleted.append(path.relative_to(ROOT).as_posix())
    for name in firecrawl.get("safe_delete", []):
        fp = FIRECRAWL / name
        if fp.is_file():
            fp.unlink()
            deleted.append(fp.relative_to(ROOT).as_posix())
    return deleted


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit dead/duplicate code in nsc-web")
    parser.add_argument(
        "--apply-safe",
        action="store_true",
        help="Delete high-confidence orphans (test.html, unused firecrawl, apply-contact-design.py)",
    )
    args = parser.parse_args()

    data = {
        "orphan_html": scan_orphan_html(),
        "scripts": scan_scripts(),
        "firecrawl": scan_firecrawl(),
        "dup_stylesheets": scan_dup_stylesheets(),
        "map_drift": scan_map_drift(),
        "placeholders": scan_placeholder_images(),
        "content_fragments": scan_content_fragments(),
    }

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {REPORT_MD.relative_to(ROOT)}")
    print(f"Wrote {REPORT_JSON.relative_to(ROOT)}")

    if args.apply_safe:
        deleted = apply_safe_deletes(data["firecrawl"])
        for d in deleted:
            print(f"Deleted {d}")
        print(f"Safe cleanup: {len(deleted)} file(s) removed")
    else:
        print("Run with --apply-safe to remove test.html, unused .firecrawl caches, apply-contact-design.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
