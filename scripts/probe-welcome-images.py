import re
import urllib.request

for path in ["/welcome/", "/about-us/", "/"]:
    html = urllib.request.urlopen("https://www.northstowesc.org" + path, timeout=20).read().decode("utf-8", "replace")
    urls = sorted(set(re.findall(r'https://www\.northstowesc\.org/wp-content/uploads/[^"\s\')]+', html)))
    print("===", path, len(urls))
    for u in urls[:40]:
        print(u)
