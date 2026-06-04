"""Stop main nav dropdowns (e.g. NSC Life) from getting an internal scrollbar."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD_CLEAR = """                siteNavigation.querySelectorAll('.nav-panel--align-right, .nav-panel--flip-left').forEach((panel) => {
                    panel.classList.remove('nav-panel--align-right', 'nav-panel--flip-left');
                    panel.style.removeProperty('max-height');
                    panel.style.removeProperty('overflow-y');
                });"""

NEW_CLEAR = """                siteNavigation.querySelectorAll('.nav-panel--align-right, .nav-panel--flip-left').forEach((panel) => {
                    panel.classList.remove('nav-panel--align-right', 'nav-panel--flip-left');
                    panel.style.removeProperty('max-height');
                    panel.style.removeProperty('overflow-y');
                    panel.style.removeProperty('transform');
                });"""

OLD_OVERFLOW = """                    if (rect.bottom > window.innerHeight - pad) {
                        panel.style.maxHeight = `${Math.max(160, window.innerHeight - rect.top - pad)}px`;
                        panel.style.overflowY = 'auto';
                    }"""

NEW_OVERFLOW = """                    if (rect.bottom > window.innerHeight - pad) {
                        if (isSubmenu) {
                            panel.style.maxHeight = `${Math.max(160, window.innerHeight - rect.top - pad)}px`;
                            panel.style.overflowY = 'auto';
                        } else {
                            let shift = rect.bottom - (window.innerHeight - pad);
                            const maxShift = Math.max(0, rect.top - pad);
                            shift = Math.min(shift, maxShift);
                            if (shift > 0) {
                                panel.style.transform = `translateY(-${shift}px)`;
                            }
                        }
                    }"""

OLD_FIT_START = """                panel.style.removeProperty('max-height');
                panel.style.removeProperty('overflow-y');
                requestAnimationFrame(() => {"""

NEW_FIT_START = """                panel.style.removeProperty('max-height');
                panel.style.removeProperty('overflow-y');
                panel.style.removeProperty('transform');
                requestAnimationFrame(() => {"""


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "setupDesktopNavPanelFlip" not in text:
        return False
    original = text
    text = text.replace(OLD_CLEAR, NEW_CLEAR)
    text = text.replace(OLD_FIT_START, NEW_FIT_START)
    text = text.replace(OLD_OVERFLOW, NEW_OVERFLOW)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if patch_file(path):
            print(f"  patched {path.relative_to(ROOT)}")
            changed += 1
    print(f"Patched {changed} file(s).")


if __name__ == "__main__":
    main()
