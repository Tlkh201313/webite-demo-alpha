"""Download essential northstowesc.org media; replace broken googleusercontent URLs only."""
from __future__ import annotations

import hashlib
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "images"
ASSETS.mkdir(parents=True, exist_ok=True)

# googleusercontent placeholders -> real URLs (small image set for welcome + about chrome)
PLACEHOLDER_MAP: dict[str, str] = {
    "https://lh3.googleusercontent.com/aida/AP1WRLtXSHuwTDdMakxRrUiyzyiLqbkBOVZdH0qglcsGMTXt4c-qzNs830UPDku6vLvw7jBg9rM8LSCl3bY4VZen5ZphyA-Qdpu3_NkArxUJQy2cpQ8OWqvuu2ZeaYEJslBmWTmRZDDk2hAMBG7lOgJsSWmRzvjvLLThw7hlYRKqPvxzpxfL2vHSvcEbml1iVhERSoPw3lZDpU-ofrSXRXQfHeLevK7IFP5FMGf-9ssPEu4iSGkjj2Tz42BNWACu": "https://www.northstowesc.org/wp-content/uploads/2022/10/NSC-Banner-5.jpg",
    "https://lh3.googleusercontent.com/aida/AP1WRLtrklJ7Ct4OdEa0Nr0V546nQYadFNoyl-02-BGtMDxH3jRAbCgPjNqu_Hpr0F5FHV6cqmFEr0WKS9uM90eOH3OTbURFtQfBS9d_8eoNoptveWD9Hyk_Ps8bTGdprC_Cu47FXVbW7KH2VaY0V3NriOxUssDWzczmIQrPGYxuv5AimzbPhpGZzB2OJVzyVQIsA2u15kp5TxRYz50ayq_nLK6ve8mug6UtzpYTPYk_a0fC9mJmn8ZOs_FnxKI": "https://www.northstowesc.org/wp-content/uploads/2022/10/NSC-Banner-5.jpg",
    "https://lh3.googleusercontent.com/aida/AP1WRLt_S70cj-DvnhlOZb6QQkP4cX1GBGoUR9kZa0Sut17zuUeDiA4UY0XDGrFJipFEAE4CCZ_uxHQHoDA7iAWYZ05wcMWfKMC0I67JsDUV7FkOSn0RBVEZOOpWAhoekpt3krIayaja6tTbvPisIrfn7SXVtrj6E8I9I0SOXgAT6lYzuuEtk5BE5lCbaVok037hrHdh-1efPtACY0xkASxXJFr51HxfLRcLBnwbUXPFsNz3r6jfN-YQ9oJsbN_g": "https://www.northstowesc.org/wp-content/uploads/2018/10/Mike-and-Andy.jpg",
    "https://lh3.googleusercontent.com/aida/AP1WRLs6H9IuoyL5C2MhSmC14-z0L-UtDJ63B7-VqPCN93fwU1ire7pbIQqBR6G20wu4vbAEfkfFa7M_GQ7jbLoDLzDOTKgv4wOrLMONaQRExU-Syor8-XCF9hFHIpvXSuGOXsQhPjf-buxVfxLotkWnQgDHTfxuAvP4JsxYw5dENpyvvOdb1wTxORYf-qDLi6-Z-VBWTcI4qTPeRcJMB-dQ5sDYNdotUml8iTM_SUQ_0aiWvFsKbX7DULxXu9E": "https://www.northstowesc.org/wp-content/themes/CMATTheme/assets/images/logo.png",
    "https://lh3.googleusercontent.com/aida-public/AB6AXuARNfzPCfTwsFKXqOLtHp153N-20N_V_WRuzu1J_pF-DjQK1EdbdSKJtw4XrG1dhQE0eLWpzwyL19_ICDPuDpMSpGcWT07XyZclW2lmr0h9urCtadvD9F5iXpS861zAIVIPUGjMeDjRsHnAV4GWyOiOn-3kvGrkIYQwr4jMfZvTrFfSJLgmVh4LoEaFqseNzjyguTUUDFKiDe-mqVp4BpT4FWDxeom4wBeBQrOBIPz4E7BQ7F4ePJQShSD9zwrwpK52fE4Y38YSUn14": "https://www.northstowesc.org/wp-content/uploads/2023/09/Logo-with-text.png",
    "https://lh3.googleusercontent.com/aida-public/AB6AXuAWPGKSMLUJSBBXu2zH62fs3hQuP3U79eqeaDTPe_05F_YOTOwzumRe_GROHXTKkHhX96YmuaQVQpAZ7myz-0EpyONf6PuGGswYdIkZEjy00NhQlc4eYDivjemfvyTPIn6nhh8LpjlOr7hyhxN6IKkJexBiGwgNobEpNmoY8gSr81vhgYRa0vX0UmuZfifISW6-5S3hD6xuuKEfWI_9evdCUz582fHHxwMIjOAVKe8yfSXilT-X1mK5tnfAXESbHuEO3Y2CQFfLom6f": "https://www.northstowesc.org/wp-content/uploads/2022/09/Logo-with-text-Meridian-Trust.png",
    "https://lh3.googleusercontent.com/aida-public/AB6AXuBXq80oShGpJ9rGWBEFxDPsbAkS3qnCHx1exsUq8sOPj3Ezq4jYHNQiWbHCHO9--MBm2Nkq7TbLZtuuUbwtmDYuIgpQq2_EP_CkkFV6kINwMXBlDX89QYdBbRCaAb5qS1S-NM_znjxBk4ePLNQycLWg4kkDKorEoutmTj68E4VJaEqgQWu0anIxUpwGAMALuniOW4BqTEwd-IyHvttZ6qcYvVJ-u14xI0MVYQDyPcGanMBaBOvFBbCWOfOF6N0PPfqTfKSVfXQuwlzm": "https://www.northstowesc.org/wp-content/uploads/2023/09/Colour-Logo-with-text.png",
}

GUSER_RE = re.compile(r"https://lh3\.googleusercontent\.com/[^\"'\s>)]+", re.I)
downloaded: dict[str, str] = {}


def asset_prefix(html_path: Path) -> str:
    depth = len(html_path.parent.relative_to(ROOT).parts)
    return ("../" * depth) if depth else ""


def local_name(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    base = Path(path).name or "image.bin"
    digest = hashlib.sha256(url.encode()).hexdigest()[:10]
    stem = Path(base).stem
    suffix = Path(base).suffix or ".jpg"
    safe = re.sub(r"[^a-zA-Z0-9._-]", "-", stem)[:80]
    return f"{safe}-{digest}{suffix}"


def download(url: str) -> str:
    url = url.split("?")[0]
    if url in downloaded:
        return downloaded[url]
    dest = ASSETS / local_name(url)
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "nsc-web-mirror/1.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        dest.write_bytes(data)
        print("saved", dest.relative_to(ROOT))
    rel = f"assets/images/{dest.name}"
    downloaded[url] = rel
    return rel


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    prefix = asset_prefix(path)

    for match in GUSER_RE.finditer(text):
        old = match.group(0)
        remote = PLACEHOLDER_MAP.get(old.split("?")[0])
        if not remote:
            continue
        asset_rel = download(remote)
        text = text.replace(old, prefix + asset_rel)

    text = re.sub(
        r'<meta\s+name="referrer"\s+content="[^"]*"\s*/?>',
        '<meta name="referrer" content="no-referrer"/>',
        text,
        count=1,
        flags=re.I,
    )
    if "name=\"referrer\"" not in text.lower() and "<head>" in text:
        text = text.replace("<head>", '<head>\n<meta name="referrer" content="no-referrer"/>', 1)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    targets = [ROOT / "welcome.html"]
    targets.extend(sorted((ROOT / "about").glob("*.html")))
    changed = 0
    for fp in targets:
        if patch_file(fp):
            print("patched", fp.relative_to(ROOT))
            changed += 1
    print(f"done: {changed} files, {len(set(downloaded.values()))} images")


if __name__ == "__main__":
    main()
