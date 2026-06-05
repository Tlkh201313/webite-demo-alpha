# Northstowe Secondary College (static demo)

Static HTML prototype of the Northstowe Secondary College website.

## Live site (GitHub Pages)

After deployment completes:

**https://Tlkh201313.github.io/webite-demo-alpha/**

Home page content is in `main.html`; the site root redirects there via `index.html`.

## Local preview

One Python host serves pages and proxies remote images/videos (northstowesc.org, etc.):

```powershell
cd C:\Users\USER\Desktop\vibecoding-websites\nsc-web
python serve.py 8080
```

Or: `.\serve.ps1 8080`

Open http://127.0.0.1:8080/main.html — external media is fetched through `/__media` and cached under `assets/_proxy_cache/`.

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
3. Open https://github.com/Tlkh201313/webite-demo-alpha/actions — open the failed **Deploy to GitHub Pages** run, expand the red step, and read the error (often **Configure Pages** failed before step 2 was done)
4. Click **Re-run all jobs** on the latest workflow run (or push any commit to `main`)

Do **not** click **Configure** on the suggested “Static HTML” or Jekyll cards on the Pages settings page; this repo already uses `.github/workflows/deploy-pages.yml`.

## Repository

https://github.com/Tlkh201313/webite-demo-alpha
