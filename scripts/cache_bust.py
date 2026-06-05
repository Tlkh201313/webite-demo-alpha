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
        updated = content.replace('nsc-responsive.css?v=6"', 'nsc-responsive.css?v=7"')
        updated = content.replace('nsc-responsive.css?v=3"', 'nsc-responsive.css?v=7"')
        updated = content.replace('nsc-responsive.css"', 'nsc-responsive.css?v=7"')
        updated = content.replace('nsc-responsive.js?v=6"', 'nsc-responsive.js?v=7"')
        updated = content.replace('nsc-responsive.js"', 'nsc-responsive.js?v=7"')
        updated = content.replace('nsc-skeleton.css?v=6"', 'nsc-skeleton.css?v=7"')
        updated = content.replace('nsc-skeleton.css"', 'nsc-skeleton.css?v=7"')
        updated = content.replace('nsc-reveal.css?v=6"', 'nsc-reveal.css?v=7"')
        updated = content.replace('nsc-reveal.css"', 'nsc-reveal.css?v=7"')
        updated = content.replace('site-chrome.css?v=6"', 'site-chrome.css?v=7"')
        updated = content.replace('site-chrome.css"', 'site-chrome.css?v=7"')
        updated = content.replace('site-content.css?v=6"', 'site-content.css?v=7"')
        updated = content.replace('site-content.css"', 'site-content.css?v=7"')
        updated = content.replace('nsc-secure-login.css?v=6"', 'nsc-secure-login.css?v=7"')
        updated = content.replace('nsc-secure-login.css"', 'nsc-secure-login.css?v=7"')
        if updated != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(updated)
            c += 1
    except Exception as e:
        print(f'Error on {f}: {e}')
print(f'Cache busted {c} files.')
