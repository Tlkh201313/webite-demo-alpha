import re
import urllib.request

for path in ("/welcome/", "/about/about-us/", "/"):
    page = urllib.request.urlopen("https://www.northstowesc.org" + path, timeout=25).read().decode("utf-8", "replace")
    print("===", path, "===")
    for u in sorted(
        set(
            re.findall(
                r"https://www\.northstowesc\.org/wp-content/uploads/[^\s\"'<>?#]+\.(?:jpe?g|png|webp|gif|mp4|mov)",
                page,
                re.I,
            )
        )
    ):
        print(u)
