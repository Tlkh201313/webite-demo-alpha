# Northstowe Secondary College (static demo)

Static HTML prototype of the Northstowe Secondary College website.

## Live site (GitHub Pages)

After deployment completes:

**https://Tlkh201313.github.io/webite-demo-alpha/**

Home page content is in `main.html`; the site root redirects there via `index.html`.

## Local preview

```powershell
cd C:\Users\USER\Desktop\vibecoding-websites\nsc-web
python -m http.server 3456
```

Open http://127.0.0.1:3456/main.html

## Deploy updates

Push to the `main` branch on GitHub; the [Deploy to GitHub Pages](.github/workflows/deploy-pages.yml) workflow publishes automatically.

```powershell
git add -A
git commit -m "Your message"
git push origin main
```

## First-time GitHub Pages setup

If the site does not appear after the first push:

1. Open https://github.com/Tlkh201313/webite-demo-alpha/settings/pages
2. Under **Build and deployment**, set **Source** to **GitHub Actions**
3. Re-run the workflow from the **Actions** tab if needed

## Repository

https://github.com/Tlkh201313/webite-demo-alpha
