"""List wp-content/uploads images from a northstowesc.org page."""
import html as html_lib
import re
import sys
import urllib.request

path = sys.argv[1] if len(sys.argv) > 1 else "/about/about-us/"
html = urllib.request.urlopen("https://www.northstowesc.org" + path, timeout=25).read().decode("utf-8", "replace")
html = html_lib.unescape(html)

urls = set()
for pat in [
    r'(?:data-lazy-src|src|href)=["\']([^"\']+wp-content/uploads[^"\']+)["\']',
    r'url\(["\']?(https://[^"\')]+wp-content/uploads[^"\')]+)',
]:
    for u in re.findall(pat, html, re.I):
        u = u.split("?")[0].replace("&amp;", "&")
        if re.search(r"\.(jpe?g|png|gif|webp|svg)$", u, re.I):
            urls.add(u)

for u in sorted(urls):
    print(u)
