"""Replace mental-health-wellbeing.html entry-content with formatted markup."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "nsc-life" / "mental-health-wellbeing.html"
CONTENT = ROOT / "scripts" / "mental-health-wellbeing-content.html"


def main() -> None:
    page = PAGE.read_text(encoding="utf-8")
    content = CONTENT.read_text(encoding="utf-8").strip()
    new_page, n = re.subn(
        r'<div class="entry-content learning-stagger">.*?</div>\s*</article>',
        content + "\n</article>",
        page,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"replace failed: {n}")
    PAGE.write_text(new_page, encoding="utf-8")
    print("updated", PAGE.relative_to(ROOT))


if __name__ == "__main__":
    main()
