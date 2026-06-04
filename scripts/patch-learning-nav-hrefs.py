"""Prefix Learning submenu hrefs with correct path to learning/ from each HTML file."""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEARNING = ROOT / "learning"

# Top-level pages under learning/ (nav uses paths relative to learning/)
LEARNING_REL = (
    "curriculum",
    "enrichment",
    "examinations",
    "homework-prep",
    "interventions",
    "progress-and-assessment",
    "remote-learning",
    "teaching-and-learning-strategy",
    "whole-school-fluency",
    "year-11-masterclasses",
)

HREF_RE = re.compile(r'href="([^"]+)"')


def learning_prefix(html_path: Path) -> str:
    rel = Path(os.path.relpath(LEARNING, html_path.parent))
    if rel == Path("."):
        return ""
    return rel.as_posix() + "/"


def needs_learning_prefix(href: str, prefix: str) -> str | None:
    if not href or href.startswith(("#", "http://", "https://", "mailto:", "tel:")):
        return None
    if "/learning/" in href or href.startswith("learning/"):
        return None
    if prefix and href.startswith(prefix.rstrip("/")):
        return None
    for stem in LEARNING_REL:
        if href == stem or href.startswith(f"{stem}.html"):
            return prefix + href
        if href.startswith(f"{stem}/"):
            return prefix + href
    return None


def patch_file(path: Path) -> bool:
    prefix = learning_prefix(path)
    if not prefix:
        return False

    text = path.read_text(encoding="utf-8")
    changed = False

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        href = match.group(1)
        fixed = needs_learning_prefix(href, prefix)
        if fixed and fixed != href:
            changed = True
            return f'href="{fixed}"'
        return match.group(0)

    new_text = HREF_RE.sub(repl, text)
    if changed:
        path.write_text(new_text, encoding="utf-8", newline="\n")
    return changed


def main() -> None:
    changed = 0
    for fp in sorted(ROOT.rglob("*.html")):
        if ".firecrawl" in fp.parts or "graphify-out" in fp.parts or fp.parent == ROOT / "scripts":
            continue
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"Patched learning nav hrefs in {changed} file(s)")


if __name__ == "__main__":
    main()
