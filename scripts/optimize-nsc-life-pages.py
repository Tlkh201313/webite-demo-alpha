"""Speed + polish pass for all nsc-life/**/*.html pages."""
from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NSC_LIFE = ROOT / "nsc-life"
SHARED_CSS = ROOT / "learning" / "learning-content.css"

_opt_spec = spec_from_file_location(
    "optimize_learning_pages",
    ROOT / "scripts" / "optimize-learning-pages.py",
)
_opt = module_from_spec(_opt_spec)
assert _opt_spec.loader is not None
sys.modules["optimize_learning_pages"] = _opt
_opt_spec.loader.exec_module(_opt)


def css_href(html_path: Path) -> str:
    return Path(
        __import__("os").path.relpath(SHARED_CSS, html_path.parent)
    ).as_posix()


def patch_file(path: Path) -> bool:
    return _opt.patch_file(path, css_base=SHARED_CSS)


def main() -> None:
    changed = 0
    for fp in sorted(NSC_LIFE.rglob("*.html")):
        if patch_file(fp):
            print(fp.relative_to(ROOT))
            changed += 1
    print(f"optimized {changed} nsc-life file(s)")


if __name__ == "__main__":
    main()
