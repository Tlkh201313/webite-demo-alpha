#!/usr/bin/env python3
"""Fix YouTube Error 153: allow referrer + origin on embed URLs."""
import glob
from pathlib import Path

META_OLD = '<meta name="referrer" content="no-referrer"/>'
META_NEW = '<meta name="referrer" content="strict-origin-when-cross-origin"/>'

IFRAME_OLD = "iframe.referrerPolicy = 'no-referrer';"
IFRAME_NEW = "iframe.referrerPolicy = 'strict-origin-when-cross-origin';"

BUILD_VARIANTS = [
    """const buildYouTubeEmbedUrl = (videoId, { autoplay = false } = {}) => {
            let url = `https://www.youtube.com/embed/${videoId}`;
            if (autoplay) url += '?autoplay=1';
            return url;
        };""",
    """const buildYouTubeEmbedUrl = (videoId, { autoplay = false } = {}) => {
            let url = `https://www.youtube.com/embed/${videoId}`;
            if (autoplay) {
                url += '?autoplay=1';
            }
            return url;
        };""",
]

BUILD_NEW = """const buildYouTubeEmbedUrl = (videoId, { autoplay = false } = {}) => {
            const origin = (location.protocol === 'file:' || !location.origin || location.origin === 'null')
                ? 'https://tlkh201313.github.io'
                : location.origin;
            const params = new URLSearchParams({
                rel: '0',
                modestbranding: '1',
                playsinline: '1',
                origin,
            });
            if (autoplay) params.set('autoplay', '1');
            return `https://www.youtube.com/embed/${videoId}?${params.toString()}`;
        };"""

ABOUT_US_COMMENT = "        // Match northstowesc.org WordPress oembed (no origin param ? live welcome film uses plain /embed/ID)\n"


def main() -> None:
    meta_count = 0
    build_count = 0
    iframe_count = 0

    for path in glob.glob("**/*.html", recursive=True):
        if ".git" in path:
            continue
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        updated = text

        if META_OLD in updated:
            updated = updated.replace(META_OLD, META_NEW)
            meta_count += 1

        if IFRAME_OLD in updated:
            updated = updated.replace(IFRAME_OLD, IFRAME_NEW)
            iframe_count += updated.count(IFRAME_NEW) - text.count(IFRAME_NEW)

        updated = updated.replace(ABOUT_US_COMMENT, "")

        for old in BUILD_VARIANTS:
            if old in updated:
                updated = updated.replace(old, BUILD_NEW)
                build_count += 1

        if updated != text:
            file_path.write_text(updated, encoding="utf-8")
            print(path)

    print(f"meta: {meta_count}, buildFn: {build_count}, iframe: {iframe_count}")


if __name__ == "__main__":
    main()
