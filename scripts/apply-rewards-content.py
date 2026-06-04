"""Replace rewards-and-sanctions.html entry area with formatted markup."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "nsc-life" / "rewards-and-sanctions.html"
CONTENT = ROOT / "scripts" / "rewards-and-sanctions-content.html"
BANNER_OLD = (
    'src="https://www.northstowesc.org/wp-content/uploads/2025/04/Banner-14.png?is-pending-load=1"'
)
BANNER_NEW = (
    'src="https://i0.wp.com/www.northstowesc.org/wp-content/uploads/2025/04/Banner-14.png'
    '?resize=1200%2C267&amp;ssl=1"'
)


def main() -> None:
    page = PAGE.read_text(encoding="utf-8")
    content = CONTENT.read_text(encoding="utf-8").strip()
    new_page, n = re.subn(
        r'<header class="entry-header">.*?</header>\s*<div class="entry-content learning-stagger">.*?</div>\s*</article>',
        content + "\n</article>",
        page,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"replace failed: {n}")
    new_page = new_page.replace(BANNER_OLD, BANNER_NEW)
    new_page = new_page.replace(
        ".entry-content .download-card a {\n                text-decoration: none;\n            }",
        ".entry-content .download-card a,\n            .entry-content .rs-policy-cta__link,\n            .entry-content .rs-highlight-card {\n                text-decoration: none;\n            }",
        1,
    )
    stagger_child = (
        "entry.target.querySelectorAll('.reveal-stagger-child, .british-value-pill')"
    )
    if stagger_child in new_page:
        new_page = new_page.replace(
            stagger_child,
            "entry.target.querySelectorAll('.reveal-stagger-child, .british-value-pill, .rs-value-pill')",
            1,
        )
    PAGE.write_text(new_page, encoding="utf-8")
    print("updated", PAGE.relative_to(ROOT))


if __name__ == "__main__":
    main()
