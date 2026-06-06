#!/usr/bin/env python3
import glob
import re
from pathlib import Path

LOGO_PATTERN = re.compile(
    r'(<img alt="Northstowe Secondary College Logo" class="h-12 sm:h-16 w-auto object-contain) '
    r'mix-blend-lighten(" src=")([^"]*?)logo-3d91fc1531\.png(")'
)


def main() -> None:
    for path in glob.glob("**/*.html", recursive=True):
        if ".git" in path:
            continue
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        updated = LOGO_PATTERN.sub(
            r"\1\2\3logo-masthead-transparent.png\4",
            text,
        )
        updated = re.sub(
            r"nsc-responsive\.(css|js)\?v=9",
            lambda m: f"nsc-responsive.{m.group(1)}?v=10",
            updated,
        )
        if updated != text:
            file_path.write_text(updated, encoding="utf-8")
            print(path)


if __name__ == "__main__":
    main()
