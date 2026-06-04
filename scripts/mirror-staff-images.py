"""Download staff photos locally and rewrite about/staff-data.json image paths."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "about" / "staff-data.json"
STAFF_DIR = ROOT / "assets" / "staff"
IMAGES_DIR = ROOT / "assets" / "images"
LOCAL_PREFIX = "../assets/staff/"


def origin_url(url: str) -> str:
    base = url.split("?")[0].strip()
    if "i0.wp.com/www." in base:
        return base.replace("https://i0.wp.com/www.", "https://www.")
    return base


def local_basename(url: str) -> str:
    path = urllib.parse.urlparse(origin_url(url)).path
    return Path(path).name


def find_existing(url: str) -> Path | None:
    """Reuse a file already mirrored under assets/images/."""
    base = local_basename(url)
    stem = Path(base).stem
    for folder in (IMAGES_DIR, STAFF_DIR):
        if not folder.is_dir():
            continue
        for candidate in folder.iterdir():
            if not candidate.is_file():
                continue
            name = candidate.name
            if name == base or name.startswith(stem + "-") or name.startswith(stem + "."):
                return candidate
    return None


def download(url: str) -> str:
    base = local_basename(url)
    dest = STAFF_DIR / base
    if dest.exists() and dest.stat().st_size > 0:
        return base

    existing = find_existing(url)
    if existing and existing.parent != STAFF_DIR:
        STAFF_DIR.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(existing.read_bytes())
        print("copied", existing.name, "->", base)
        return base

    fetch_url = origin_url(url)
    STAFF_DIR.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(fetch_url, headers={"User-Agent": "nsc-web-staff-mirror/1.0"})
    try:
        data = urllib.request.urlopen(req, timeout=90).read()
    except Exception:
        # Some live paths use -scaled suffix only on CDN mirror
        if "-scaled." not in fetch_url:
            alt = re.sub(r"(\.[^./]+)$", r"-scaled\1", fetch_url)
            req = urllib.request.Request(alt, headers={"User-Agent": "nsc-web-staff-mirror/1.0"})
            data = urllib.request.urlopen(req, timeout=90).read()
        else:
            raise
    dest.write_bytes(data)
    print("saved", base, len(data))
    return base


def main() -> None:
    staff = json.loads(DATA.read_text(encoding="utf-8"))
    seen: dict[str, str] = {}

    for section in staff:
        for member in section.get("members", []):
            url = member.get("image")
            if not url or url.startswith("../assets/"):
                continue
            key = origin_url(url)
            if key not in seen:
                seen[key] = download(url)
            member["image"] = LOCAL_PREFIX + seen[key]

    DATA.write_text(json.dumps(staff, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated {DATA} ({len(seen)} images)")


if __name__ == "__main__":
    main()
