"""Fix Jetpack lazy-load img markup in existing HTML files."""
from __future__ import annotations

import html as html_lib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fix_lazy_images(content: str) -> str:
    def fix_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        lazy_src = re.search(r'data-lazy-src="([^"]*)"', tag, re.I)
        lazy_srcset = re.search(r'data-lazy-srcset="([^"]*)"', tag, re.I)
        lazy_sizes = re.search(r'data-lazy-sizes="([^"]*)"', tag, re.I)

        if lazy_src:
            src = html_lib.unescape(lazy_src.group(1)).replace("&#038;", "&")
            if re.search(r'\ssrc="', tag, re.I):
                tag = re.sub(r'\ssrc="[^"]*"', f' src="{src}"', tag, count=1, flags=re.I)
            else:
                tag = re.sub(r"<img\b", f'<img src="{src}"', tag, count=1, flags=re.I)

        if lazy_srcset:
            srcset = html_lib.unescape(lazy_srcset.group(1)).replace("&#038;", "&")
            tag = re.sub(r'\ssrcset="[^"]*"', f' srcset="{srcset}"', tag, count=1, flags=re.I)
        elif re.search(r'\ssrcset="data:image/gif', tag, re.I):
            tag = re.sub(r'\ssrcset="[^"]*"', "", tag, count=1, flags=re.I)

        if lazy_sizes:
            sizes = html_lib.unescape(lazy_sizes.group(1))
            if re.search(r'\ssizes="', tag, re.I):
                tag = re.sub(r'\ssizes="[^"]*"', f' sizes="{sizes}"', tag, count=1, flags=re.I)
            else:
                tag = re.sub(r"<img\b", f'<img sizes="{sizes}"', tag, count=1, flags=re.I)

        tag = re.sub(r'\sdata-lazy-[^=]+="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r'\sdata-recalc-dims="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r"\sjetpack-lazy-image\b", "", tag, flags=re.I)
        tag = re.sub(r"[?&]is-pending-load=1", "", tag)
        tag = re.sub(r'\sclass="\s*"', "", tag)
        return tag

    return re.sub(r"<img\b[^>]*>", fix_img, content, flags=re.I)


def main() -> None:
    targets = list(ROOT.glob("learning/**/*.html"))
    if len(sys.argv) > 1:
        targets = [ROOT / p for p in sys.argv[1:]]
    for fp in targets:
        text = fp.read_text(encoding="utf-8")
        new = fix_lazy_images(text)
        if new != text:
            fp.write_text(new, encoding="utf-8")
            print(fp.relative_to(ROOT))
    print("done")


if __name__ == "__main__":
    main()
