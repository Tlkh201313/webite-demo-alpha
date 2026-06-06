#!/usr/bin/env python3
"""Strip hero fade-in classes and add nsc-page-hero id."""
import glob
import re
from pathlib import Path

SECTION_RE = re.compile(
    r'(<section class=")(relative h-\[[^\]]+\][^"]*flex items-center overflow-hidden)(">)'
)
OPACITY_ANIM_RE = re.compile(
    r"\s*opacity-0 animate-\[fadeInUp[^\]]+\]"
)


def main() -> None:
    for path in glob.glob("**/*.html", recursive=True):
        if ".git" in path:
            continue
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        if "flex items-center overflow-hidden" not in text:
            continue
        updated = SECTION_RE.sub(
            r'\1\2" id="nsc-page-hero">',
            text,
            count=1,
        )
        updated = OPACITY_ANIM_RE.sub("", updated)
        updated = updated.replace("text-on-primary/90", "text-on-primary")
        if updated != text:
            file_path.write_text(updated, encoding="utf-8")
            print(path)


if __name__ == "__main__":
    main()
