import glob
import re

ASSETS = [
    "nsc-responsive.css",
    "nsc-responsive.js",
    "nsc-skeleton.css",
    "nsc-reveal.css",
    "site-chrome.css",
    "site-content.css",
    "nsc-secure-login.css",
]
VERSION = "7"
count = 0

for path in glob.glob("**/*.html", recursive=True):
    if ".git" in path:
        continue
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    updated = text
    for name in ASSETS:
        updated = re.sub(re.escape(name) + r"\?v=\d+", f"{name}?v={VERSION}", updated)
        updated = updated.replace(f'{name}"', f'{name}?v={VERSION}"')
        updated = updated.replace(f"{name}'", f"{name}?v={VERSION}'")
    if updated != text:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(updated)
        count += 1

print(f"Bumped {count} HTML files to v={VERSION}.")
