"""Insert .wp-block-file layout styles into learning page templates."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "learning"

OLD = """            .download-card {
                padding: 1.25rem;
                border-radius: 0.5rem;
                background: rgba(243, 235, 246, 0.5);
                border: 1px solid rgba(73, 14, 103, 0.08);
            }

            /* Nav: mobile accordion (northstowesc.org) + desktop flyouts at 48em */"""

WP_BLOCK_FILE_CSS = """            .entry-content .wp-block-file {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 0.5rem 1rem;
                margin: 1.25rem 0;
                padding: 1rem 1.25rem;
                border-radius: 0.5rem;
                background: rgba(243, 235, 246, 0.5);
                border: 1px solid rgba(73, 14, 103, 0.08);
            }
            .entry-content .wp-block-file__embed {
                flex: 1 1 100%;
                width: 100%;
                margin: 0;
                border: none;
            }
            .entry-content .wp-block-file__embed[hidden] {
                display: none;
            }
            .entry-content .wp-block-file > a:not(.wp-block-file__button) {
                font-weight: 600;
                color: #490e67;
                text-decoration: underline;
                text-underline-offset: 3px;
            }
            .entry-content .wp-block-file > a:not(.wp-block-file__button):hover {
                color: #350053;
            }
            .entry-content .wp-block-file__button {
                display: inline-flex;
                align-items: center;
                padding: 0.5rem 1rem;
                border-radius: 0.375rem;
                background: #490e67;
                color: #ffffff;
                font-family: "Hanken Grotesk", sans-serif;
                font-weight: 700;
                font-size: 0.875rem;
                line-height: 1.2;
                text-decoration: none;
                white-space: nowrap;
            }
            .entry-content .wp-block-file__button:hover {
                background: #350053;
                color: #ffffff;
            }

"""

NEW = OLD.replace(
    "\n            /* Nav:",
    "\n" + WP_BLOCK_FILE_CSS + "            /* Nav:",
    1,
)


def main() -> None:
    for path in sorted(ROOT.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        if ".entry-content .wp-block-file" in text:
            continue
        if OLD not in text:
            print(f"skip {path.relative_to(ROOT.parent)}")
            continue
        path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
        print(f"patched {path.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
