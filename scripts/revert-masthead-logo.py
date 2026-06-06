#!/usr/bin/env python3
"""Revert masthead logo to logo-3d91fc1531.png with mix-blend-lighten."""
import glob
import re
from pathlib import Path

LOGO_REVERT = re.compile(
    r'(<img alt="Northstowe Secondary College Logo" class="h-12 sm:h-16 w-auto object-contain)(?: mix-blend-lighten)?(" src=")([^"]*?)logo-masthead-transparent\.png(")'
)


def main() -> None:
    for path in glob.glob("**/*.html", recursive=True):
        if ".git" in path:
            continue
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        updated = LOGO_REVERT.sub(
            r"\1 mix-blend-lighten\2\3logo-3d91fc1531.png\4",
            text,
        )
        if updated != text:
            file_path.write_text(updated, encoding="utf-8")
            print(path)


if __name__ == "__main__":
    main()
