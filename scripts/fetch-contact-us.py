import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".firecrawl" / "contact-us-source.html"
url = "https://www.northstowesc.org/contact-us/"
req = urllib.request.Request(url, headers={"User-Agent": "nsc-web-builder/1.0"})
with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=90) as resp:
    OUT.write_bytes(resp.read())
print("wrote", OUT, "bytes", OUT.stat().st_size)
