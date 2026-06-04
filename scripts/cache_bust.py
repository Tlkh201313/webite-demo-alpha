import glob, os

files = glob.glob('**/*.html', recursive=True)
c = 0
for f in files:
    if 'graphify' in f or '.git' in f:
        continue
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        # Bump version query string
        updated = content.replace('nsc-responsive.css?v=2"', 'nsc-responsive.css?v=3"')
        updated = updated.replace('nsc-responsive.css"', 'nsc-responsive.css?v=3"')
        updated = updated.replace('nsc-skeleton.css"', 'nsc-skeleton.css?v=3"')
        updated = updated.replace('nsc-reveal.css"', 'nsc-reveal.css?v=3"')
        updated = updated.replace('site-chrome.css"', 'site-chrome.css?v=3"')
        updated = updated.replace('site-content.css"', 'site-content.css?v=3"')
        updated = updated.replace('nsc-secure-login.css"', 'nsc-secure-login.css?v=3"')
        if updated != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(updated)
            c += 1
    except Exception as e:
        print(f'Error on {f}: {e}')
print(f'Cache busted {c} files.')
