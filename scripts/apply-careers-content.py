"""Replace careers-education.html entry-content with formatted hub markup."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "nsc-life" / "careers-education.html"
CONTENT = ROOT / "scripts" / "careers-education-content.html"


def main() -> None:
    page = PAGE.read_text(encoding="utf-8")
    content = CONTENT.read_text(encoding="utf-8").strip()
    marker = '<div class="entry-content learning-stagger">'
    start = page.find(marker)
    if start < 0:
        raise SystemExit("entry-content not found")
    end = page.find("</article>", start)
    if end < 0:
        raise SystemExit("</article> not found")
    new_page = page[:start] + content + "\n" + page[end:]
    PAGE.write_text(new_page, encoding="utf-8")
    print("updated", PAGE.relative_to(ROOT))


if __name__ == "__main__":
    main()
