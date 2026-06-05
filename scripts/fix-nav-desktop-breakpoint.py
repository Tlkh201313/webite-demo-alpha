"""Align nav desktop flyout breakpoint with documented 48em (not 72em)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MOBILE_OLD = "@media (max-width: 71.99em) {\n                .site-navigation"
MOBILE_NEW = "@media (max-width: 47.99em) {\n                .site-navigation"

DESKTOP_OLD = "@media (min-width: 72em) {\n                .menu-toggle,"
DESKTOP_NEW = "@media (min-width: 48em) {\n                .menu-toggle,"

MQ_OLD = "matchMedia('(min-width: 72em)')"
MQ_NEW = "matchMedia('(min-width: 48em)')"

RESPONSIVE_OLD = "@media (min-width: 72em) and (max-width: 63.99em)"
RESPONSIVE_NEW = "@media (min-width: 48em) and (max-width: 63.99em)"


def patch_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    original = text
    changes: list[str] = []

    if MOBILE_OLD in text:
        text = text.replace(MOBILE_OLD, MOBILE_NEW)
        changes.append("mobile nav max-width 47.99em")

    if DESKTOP_OLD in text:
        text = text.replace(DESKTOP_OLD, DESKTOP_NEW)
        changes.append("desktop nav min-width 48em")

    if MQ_OLD in text:
        text = text.replace(MQ_OLD, MQ_NEW)
        changes.append("desktopNavMq 48em")

    if text != original:
        path.write_text(text, encoding="utf-8")
    return changes


def main() -> None:
    touched = 0
    for path in sorted(ROOT.rglob("*.html")):
        changes = patch_file(path)
        if changes:
            touched += 1
            print(f"{path.relative_to(ROOT)}: {', '.join(changes)}")

    resp = ROOT / "nsc-responsive.css"
    resp_text = resp.read_text(encoding="utf-8")
    if RESPONSIVE_OLD in resp_text:
        resp.write_text(resp_text.replace(RESPONSIVE_OLD, RESPONSIVE_NEW), encoding="utf-8")
        print("nsc-responsive.css: tablet range 48em–63.99em")

    print(f"\nPatched {touched} HTML file(s).")


if __name__ == "__main__":
    main()
