"""Rebuild broken Learning page sidebars from build-learning-pages.sidebar_html."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "build_learning_pages",
    ROOT / "scripts" / "build-learning-pages.py",
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
PAGES = _mod.PAGES
sidebar_html = _mod.sidebar_html

ASIDE_RE = re.compile(
    r'<aside class="nsc-page-sidebar"[^>]*>.*?</aside>',
    re.DOTALL,
)


def slug_for_path(rel: str) -> str | None:
    for out_path, _, slug in PAGES:
        if out_path == rel:
            return slug
    if rel == "learning/curriculum/subjects.html":
        return "subjects"
    if rel == "learning/curriculum/celebrating-diversity.html":
        return "celebrating-diversity"
    return None


def rebuild_aside(fp: Path) -> bool:
    rel = fp.relative_to(ROOT).as_posix()
    slug = slug_for_path(rel)
    if slug is None:
        return False
    text = fp.read_text(encoding="utf-8")
    new_inner = sidebar_html(fp, slug, rel)
    new_aside = f'<aside class="nsc-page-sidebar" aria-label="Curriculum section">\n{new_inner}\n</aside>'
    if "learning/curriculum/subjects/" not in rel and not rel.startswith("learning/curriculum/"):
        new_aside = new_aside.replace(
            'aria-label="Curriculum section"',
            'aria-label="Learning section"',
        )
    new_text, n = ASIDE_RE.subn(new_aside, text, count=1)
    if n == 0:
        return False
    if new_text != text:
        fp.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    for fp in sorted(ROOT.glob("learning/**/*.html")):
        if rebuild_aside(fp):
            print("rebuilt", fp.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
