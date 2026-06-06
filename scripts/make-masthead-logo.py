#!/usr/bin/env python3
"""Create a masthead logo PNG with transparent purple background."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "NSC_Logo.png"
OUT = ROOT / "assets" / "images" / "logo-masthead-transparent.png"


def is_white(r: int, g: int, b: int) -> bool:
    return r > 210 and g > 210 and b > 210


def is_purple_bg(r: int, g: int, b: int) -> bool:
    if is_white(r, g, b):
        return False
    # Logo background + internal divider lines (same purple family)
    return b > 45 and r > 25 and g < max(r, b) * 0.45


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing source logo: {SRC}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(SRC).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if is_purple_bg(r, g, b):
                pixels[x, y] = (r, g, b, 0)

    img.save(OUT, optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
