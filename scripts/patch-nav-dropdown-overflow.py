"""Keep desktop nav flyouts on-screen when nested submenus would overflow."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSS_MARKER = """                .nav-dropdown-panel .sub-chevron {
                    display: inline;
                    font-size: 1.125rem;
                    opacity: 0.9;
                    flex-shrink: 0;
                }
            }

            @media (min-width: 64em) {"""

CSS_REPLACEMENT = """                .nav-dropdown-panel .sub-chevron {
                    display: inline;
                    font-size: 1.125rem;
                    opacity: 0.9;
                    flex-shrink: 0;
                }
                .nav-dropdown-panel.nav-panel--align-right {
                    left: auto;
                    right: 0;
                }
                .nav-dropdown-panel .submenu-panel.nav-panel--flip-left {
                    left: auto;
                    right: 100%;
                }
            }

            @media (min-width: 64em) {"""

JS_MARKER = "        setupMobileNavToggles();\n"
JS_REPLACEMENT = """        setupMobileNavToggles();

        function setupDesktopNavPanelFlip() {
            if (!siteNavigation) {
                return;
            }

            function clearNavPanelFlip() {
                siteNavigation.querySelectorAll('.nav-panel--align-right, .nav-panel--flip-left').forEach((panel) => {
                    panel.classList.remove('nav-panel--align-right', 'nav-panel--flip-left');
                    panel.style.removeProperty('max-height');
                    panel.style.removeProperty('overflow-y');
                    panel.style.removeProperty('transform');
                });
            }

            function fitNavPanel(panel) {
                if (!desktopNavMq.matches || !panel) {
                    return;
                }
                panel.classList.remove('nav-panel--align-right', 'nav-panel--flip-left');
                panel.style.removeProperty('max-height');
                panel.style.removeProperty('overflow-y');
                panel.style.removeProperty('transform');
                requestAnimationFrame(() => {
                    const pad = 12;
                    let rect = panel.getBoundingClientRect();
                    const isSubmenu = panel.classList.contains('submenu-panel');
                    if (rect.right > window.innerWidth - pad) {
                        panel.classList.add(isSubmenu ? 'nav-panel--flip-left' : 'nav-panel--align-right');
                        rect = panel.getBoundingClientRect();
                    }
                    if (isSubmenu && rect.left < pad) {
                        panel.classList.remove('nav-panel--flip-left');
                    }
                    if (rect.bottom > window.innerHeight - pad) {
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
                    }
                });
            }

            siteNavigation.querySelectorAll('.nav-menu-item').forEach((item) => {
                const panel = item.querySelector(':scope > .nav-dropdown-panel');
                if (!panel) {
                    return;
                }
                const onOpen = () => {
                    clearNavPanelFlip();
                    fitNavPanel(panel);
                };
                item.addEventListener('mouseenter', onOpen);
                item.addEventListener('focusin', onOpen);
            });

            siteNavigation.querySelectorAll('li.has-children').forEach((item) => {
                const sub = item.querySelector(':scope > .submenu-panel');
                if (!sub) {
                    return;
                }
                const onOpen = () => fitNavPanel(sub);
                item.addEventListener('mouseenter', onOpen);
                item.addEventListener('focusin', onOpen);
            });

            siteNavigation.addEventListener('mouseleave', clearNavPanelFlip);
            window.addEventListener('resize', clearNavPanelFlip);
        }

        setupDesktopNavPanelFlip();
"""


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    if "nav-panel--flip-left" not in text and CSS_MARKER in text:
        text = text.replace(CSS_MARKER, CSS_REPLACEMENT, 1)

    if "setupDesktopNavPanelFlip" not in text and JS_MARKER in text:
        text = text.replace(JS_MARKER, JS_REPLACEMENT, 1)

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
