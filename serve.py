#!/usr/bin/env python3
"""
NSC unified local host — one process for static pages + remote media.

Serves the static site and proxies images, videos, and other allowlisted
remote assets through /__media so pages do not each depend on separate hosts.

Usage:
    python serve.py              # default port 8080
    python serve.py 3456
"""
from __future__ import annotations

import argparse
import hashlib
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from http import HTTPStatus
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "assets" / "_proxy_cache"
USER_AGENT = "nsc-web-serve/1.0"

# Hosts routed through this server (single local origin)
PROXY_HOSTS = frozenset(
    {
        "www.northstowesc.org",
        "northstowesc.org",
        "lh3.googleusercontent.com",
        "i.ytimg.com",
        "img.youtube.com",
    }
)

# Rewrite https://… in HTML/CSS when served locally
REMOTE_URL_RE = re.compile(
    r"https://(?:(?:www\.)?northstowesc\.org|lh3\.googleusercontent\.com|"
    r"i\.ytimg\.com|img\.youtube\.com)"
    r"[^\s\"'<>)]*",
    re.IGNORECASE,
)

HTML_LIKE = {".html", ".htm"}
TEXT_LIKE = HTML_LIKE | {".css", ".js"}


def is_proxy_host(netloc: str) -> bool:
    host = netloc.lower().split(":", 1)[0]
    if host in PROXY_HOSTS:
        return True
    return host.endswith(".googleusercontent.com")


def proxy_path(remote_url: str) -> str:
    return "/__media?url=" + urllib.parse.quote(remote_url, safe="")


def rewrite_remote_urls(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return proxy_path(match.group(0))

    return REMOTE_URL_RE.sub(repl, text)


def cache_path_for(url: str) -> Path:
    parsed = urllib.parse.urlparse(url)
    name = Path(parsed.path).name or "asset.bin"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    stem = re.sub(r"[^a-zA-Z0-9._-]", "-", Path(name).stem)[:60]
    suffix = Path(name).suffix or ".bin"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{stem}-{digest}{suffix}"


def fetch_remote(url: str, timeout: int = 120) -> tuple[bytes, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        ctype = resp.headers.get("Content-Type")
        return data, ctype


def load_cached(url: str) -> tuple[Path, str | None] | None:
    path = cache_path_for(url)
    meta = path.with_suffix(path.suffix + ".meta")
    if not path.exists():
        return None
    ctype = None
    if meta.exists():
        ctype = meta.read_text(encoding="utf-8").strip() or None
    return path, ctype


def store_cached(url: str, data: bytes, content_type: str | None) -> Path:
    path = cache_path_for(url)
    path.write_bytes(data)
    if content_type:
        meta = path.with_suffix(path.suffix + ".meta")
        meta.write_text(content_type.split(";")[0].strip(), encoding="utf-8")
    return path


def guess_type(path: Path, header_type: str | None) -> str:
    if header_type:
        return header_type.split(";")[0].strip()
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def read_range(path: Path, start: int, end: int) -> bytes:
    with path.open("rb") as fh:
        fh.seek(start)
        return fh.read(end - start + 1)


class NSCHandler(SimpleHTTPRequestHandler):
    """Static files + /__media proxy + HTML URL rewriting."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        if args and isinstance(args[0], str) and args[0].startswith("/__media"):
            return
        super().log_message(fmt, *args)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/__media":
            self._serve_media(parsed)
            return
        if parsed.path in ("", "/"):
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/main.html")
            self.end_headers()
            return
        return super().do_GET()

    def _serve_media(self, parsed: urllib.parse.ParseResult) -> None:
        qs = urllib.parse.parse_qs(parsed.query)
        raw_urls = qs.get("url") or []
        if not raw_urls:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing url query parameter")
            return
        remote_url = raw_urls[0]
        remote = urllib.parse.urlparse(remote_url)
        if remote.scheme not in ("http", "https") or not is_proxy_host(remote.netloc):
            self.send_error(HTTPStatus.FORBIDDEN, "Host not allowlisted")
            return

        cached = load_cached(remote_url)
        if cached is None:
            try:
                data, ctype = fetch_remote(remote_url)
            except urllib.error.HTTPError as exc:
                self.send_error(exc.code, f"Upstream error: {exc.reason}")
                return
            except urllib.error.URLError as exc:
                self.send_error(HTTPStatus.BAD_GATEWAY, str(exc.reason))
                return
            path = store_cached(remote_url, data, ctype)
            content_type = guess_type(path, ctype)
        else:
            path, ctype = cached
            content_type = guess_type(path, ctype)

        size = path.stat().st_size
        range_header = self.headers.get("Range")
        if range_header and range_header.startswith("bytes="):
            self._send_range(path, size, content_type, range_header)
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        with path.open("rb") as fh:
            while chunk := fh.read(1024 * 64):
                self.wfile.write(chunk)

    def _send_range(
        self, path: Path, size: int, content_type: str, range_header: str
    ) -> None:
        try:
            spec = range_header.replace("bytes=", "").split("-", 1)
            start = int(spec[0]) if spec[0] else 0
            end = int(spec[1]) if spec[1] else size - 1
        except ValueError:
            self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            return
        end = min(end, size - 1)
        if start > end or start >= size:
            self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            return
        chunk = read_range(path, start, end)
        self.send_response(HTTPStatus.PARTIAL_CONTENT)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(chunk)))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        self.wfile.write(chunk)

    def send_head(self) -> object | None:
        path = self.translate_path(self.path)
        path_obj = Path(path)
        suffix = path_obj.suffix.lower()

        if suffix in TEXT_LIKE and path_obj.is_file():
            try:
                raw = path_obj.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return super().send_head()
            if suffix in HTML_LIKE or suffix == ".css":
                raw = rewrite_remote_urls(raw)
            body = raw.encode("utf-8")
            ctype = "text/html; charset=utf-8" if suffix in HTML_LIKE else "text/css; charset=utf-8"
            if suffix == ".js":
                ctype = "application/javascript; charset=utf-8"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self._text_body = body
            return self._text_body

        return super().send_head()

    def copyfile(self, source, outputfile) -> None:
        if hasattr(self, "_text_body"):
            outputfile.write(self._text_body)
            del self._text_body
            return
        super().copyfile(source, outputfile)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NSC unified local host")
    parser.add_argument("port", nargs="?", type=int, default=8080, help="TCP port")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address (default 127.0.0.1)",
    )
    args = parser.parse_args(argv)

    os.chdir(ROOT)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    server = ThreadingHTTPServer((args.host, args.port), NSCHandler)
    base = f"http://{args.host}:{args.port}"
    print(f"Serving {ROOT}")
    print(f"  Home:     {base}/main.html")
    print(f"  Media:    {base}/__media?url=<encoded-remote-url>")
    print("  Remote images/videos from northstowesc.org are proxied automatically.")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
