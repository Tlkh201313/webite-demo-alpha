"""Replace wrong mirrored images on welcome + about-us with URLs from northstowesc.org."""
from __future__ import annotations

import hashlib
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "images"
ASSETS.mkdir(parents=True, exist_ok=True)

# remote URL -> files to patch (path from ROOT, old local filename fragment)
REPLACEMENTS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "https://www.northstowesc.org/wp-content/uploads/2021/11/Front-of-Shcool-Professional-scaled.jpg",
        [
            ("welcome.html", "NSC-Banner-5-1c9bb89d90.jpg"),
            ("about/about-us.html", "NSC-Banner-5-1c9bb89d90.jpg"),  # learning community block only
        ],
    ),
    (
        "https://www.northstowesc.org/wp-content/uploads/2022/10/NSC-Banner-2-1.jpg",
        [
            ("about/about-us.html", "NSC-Banner-5-1c9bb89d90.jpg"),  # hero + video poster
        ],
    ),
    (
        "https://www.northstowesc.org/wp-content/uploads/2021/11/Students-PE-2-scaled.jpg",
        [
            ("about/about-us.html", "Mike-and-Andy-c931451d25.jpg"),
        ],
    ),
]


def local_name(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    base = Path(path).name or "image.bin"
    digest = hashlib.sha256(url.encode()).hexdigest()[:10]
    stem = Path(base).stem
    suffix = Path(base).suffix or ".jpg"
    safe = re.sub(r"[^a-zA-Z0-9._-]", "-", stem)[:80]
    return f"{safe}-{digest}{suffix}"


def download(url: str) -> str:
    dest = ASSETS / local_name(url)
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "nsc-web-fix/1.0"})
        dest.write_bytes(urllib.request.urlopen(req, timeout=90).read())
        print("saved", dest.name)
    return dest.name


def asset_prefix(html_path: Path) -> str:
    depth = len(html_path.parent.relative_to(ROOT).parts)
    return ("../" * depth) if depth else ""


def main() -> None:
    # First pass: build new filenames per remote URL
    url_to_file: dict[str, str] = {url: download(url) for url, _ in REPLACEMENTS}

    for url, targets in REPLACEMENTS:
        new_name = url_to_file[url]
        for rel, old_fragment in targets:
            path = ROOT / rel
            text = path.read_text(encoding="utf-8", errors="replace")
            prefix = asset_prefix(path)
            new_src = prefix + "assets/images/" + new_name

            # about-us: Banner-5 used in hero, poster, AND campus — map by context
            if rel == "about/about-us.html" and old_fragment.startswith("NSC-Banner-5"):
                campus_name = url_to_file[
                    "https://www.northstowesc.org/wp-content/uploads/2021/11/Front-of-Shcool-Professional-scaled.jpg"
                ]
                hero_name = url_to_file[
                    "https://www.northstowesc.org/wp-content/uploads/2022/10/NSC-Banner-2-1.jpg"
                ]
                campus_src = prefix + "assets/images/" + campus_name
                hero_src = prefix + "assets/images/" + hero_name
                old = prefix + "assets/images/" + old_fragment
                # hero (first occurrence in hero section)
                text = text.replace(
                    'id="hero-parallax">\n<img alt="Northstowe Secondary College campus at the education campus" class="w-full h-full object-cover z-0 scale-110 transition-transform duration-[10s] hover:scale-100" src="'
                    + old
                    + '"',
                    'id="hero-parallax">\n<img alt="Northstowe Secondary College campus at the education campus" class="w-full h-full object-cover z-0 scale-110 transition-transform duration-[10s] hover:scale-100" src="'
                    + hero_src
                    + '"',
                    1,
                )
                text = text.replace('poster="' + old + '"', 'poster="' + hero_src + '"', 1)
                text = text.replace(
                    'alt="Northstowe Learning Community campus aerial view" class="absolute inset-0 w-full h-full object-cover rounded-xl editorial-shadow interactive-hover" src="'
                    + old
                    + '"',
                    'alt="Northstowe Learning Community campus aerial view" class="absolute inset-0 w-full h-full object-cover rounded-xl editorial-shadow interactive-hover" src="'
                    + campus_src
                    + '"',
                    1,
                )
            else:
                old = prefix + "assets/images/" + old_fragment
                if old not in text:
                    print("skip missing", rel, old_fragment)
                    continue
                text = text.replace(old, new_src)

            path.write_text(text, encoding="utf-8", newline="\n")
            print("patched", rel, "->", new_name)

    # welcome.html hero only
    welcome = ROOT / "welcome.html"
    text = welcome.read_text(encoding="utf-8")
    campus_name = url_to_file[
        "https://www.northstowesc.org/wp-content/uploads/2021/11/Front-of-Shcool-Professional-scaled.jpg"
    ]
    old = "assets/images/NSC-Banner-5-1c9bb89d90.jpg"
    new = "assets/images/" + campus_name
    if old in text:
        text = text.replace(old, new, 1)  # hero only (first)
        welcome.write_text(text, encoding="utf-8", newline="\n")
        print("patched welcome.html hero ->", campus_name)

    print("done")


if __name__ == "__main__":
    main()
