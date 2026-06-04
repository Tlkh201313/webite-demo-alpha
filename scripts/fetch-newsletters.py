"""Sync newsletter items from Northstowe RSS into data/newsletters.json."""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "newsletters.json"
FEED = "https://www.northstowesc.org/category/news/newsletter/feed/"
ARCHIVE = "https://www.northstowesc.org/newsletter/"
PLACEHOLDER_IMG = (
    "https://www.northstowesc.org/wp-content/themes/CMATTheme/assets/images/placeholder-logo.jpg"
)
SSL_CTX = ssl.create_default_context()


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def parse_rss(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        return []
    items = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        desc = strip_html(item.findtext("description") or "")
        if not title or not link:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "pubDate": pub,
                "excerpt": desc or "Read the latest college newsletter.",
                "image": PLACEHOLDER_IMG,
            }
        )
    return items


def main() -> None:
    req = urllib.request.Request(FEED, headers={"User-Agent": "nsc-web-newsletters/1.0"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as resp:
        items = parse_rss(resp.read())
    payload = {
        "fetchedAt": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archiveUrl": ARCHIVE,
        "items": items[:10],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(payload['items'])} items to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
