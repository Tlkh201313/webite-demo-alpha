import html as h
import re
from pathlib import Path

raw = Path(__file__).resolve().parents[1] / ".firecrawl" / "pandesports-northstowe.html"
text = raw.read_text(encoding="utf-8", errors="replace")

for tag in ("h1", "h2", "h3", "h4", "p", "li", "a"):
    for m in re.finditer(rf"<{tag}[^>]*>(.*?)</{tag}>", text, re.I | re.S):
        s = re.sub(r"<[^>]+>", " ", m.group(1))
        s = h.unescape(re.sub(r"\s+", " ", s)).strip()
        if len(s) < 8 or "{" in s or "@media" in s:
            continue
        print(f"[{tag}] {s[:240]}")

print("\n--- imgs ---")
for m in re.finditer(r'(?:src|data-src|srcset)="([^"]+)"', text):
    u = m.group(1)
    if "img" in u or "jpg" in u or "png" in u or "webp" in u:
        print(u[:160])
