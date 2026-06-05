"""Repair U+FFFD replacement characters introduced by errors='replace' reads."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Order matters: specific patterns before generic fallbacks.
RULES: list[tuple[str, str]] = [
    (r"official site\) \ufffd link", "official site) — link"),
    (r'<p class="">\ufffd Northstowe Secondary College', '<p class="">© Northstowe Secondary College'),
    (r"Loading vacancies\ufffd", "Loading vacancies…"),
    (r"northstowesc\.org \ufffd do not", "northstowesc.org — do not"),
    (r"YouTube embeds \ufffd Error", "YouTube embeds — Error"),
    (r"place stat cards \ufffd editorial", "place stat cards – editorial"),
    (r"Learning Community \ufffd follow", "Learning Community – follow"),
    (r"Phase 2 launch \ufffd Sixth", "Phase 2 launch – Sixth"),
    (r"pre-school \ufffd developed", "pre-school – developed"),
    (r"Architects\ufffd 3D", "Architects' 3D"),
    (r"Northstowe\ufffds", "Northstowe's"),
    (r"~\ufffd45m", "~£45m"),
    (r"approved \ufffd Phase", "approved – Phase"),
    (r"campus looks now \ufffd visit", "campus looks now – visit"),
    (r"at Northstowe \ufffd early", "at Northstowe – early"),
    (r"Community \ufffd secondary", "Community – secondary"),
    (r"Year 7 pupils \ufffd build", "Year 7 pupils – build"),
    (r"shapes Northstowe\ufffds new", "shapes Northstowe's new"),
    (r"Minutes \ufffd ", "Minutes – "),
    (r"Ethnicity Data \ufffd ", "Ethnicity Data – "),
    (r"March \ufffd read", "March — read"),
    (r"March \ufffd four", "March — four"),
    (r"inspection \ufffd four", "inspection — four"),
    (r"inspection in March \ufffd read", "inspection in March — read"),
    (r"Hardworking \ufffd our", "Hardworking — our"),
    (r"Hardworking \ufffd the", "Hardworking — the"),
    (r"Hardworking \ufffd Northstowe", "Hardworking — Northstowe"),
    (r"your limit \ufffd the", "your limit — the"),
    (r"Be Northstowe&rsquo; \ufffd clear", "Be Northstowe&rsquo; — clear"),
    (r"staff \ufffd sharing", "staff — sharing"),
    (r"everything right \ufffd we", "everything right — we"),
    (r"it right we praise \ufffd the", "it right we praise — the"),
    (r"We did \ufffd parent", "We did — parent"),
    (r"pitches \ufffd thank", "pitches — thank"),
    (r"communities \ufffd Northstowe", "communities — Northstowe"),
    (r"our community \ufffd and that", "our community — and that"),
    (r"at Northstowe \ufffd a new", "at Northstowe — a new"),
    (r"entire area \ufffd from", "entire area — from"),
    (r"as we grow \ufffd working", "as we grow — working"),
    (r"within Meridian Trust \ufffd monitoring", "within Meridian Trust — monitoring"),
    (r"our communities \ufffd Northstowe", "our communities — Northstowe"),
    (r"heart of our communities \ufffd Northstowe", "heart of our communities — Northstowe"),
    (r"our community \ufffd and that desire", "our community — and that desire"),
    (r"education for all at the heart of our communities \ufffd Northstowe", "education for all at the heart of our communities — Northstowe"),
    (r"<span class=\"quote-block block pl-4 my-3 italic\">\ufffd", '<span class="quote-block block pl-4 my-3 italic">"'),
    (r"community\ufffd pupils", "community— pupils"),
    (r"environment.\ufffd</span>", 'environment."</span>'),
    (r"first day\ufffd looking", "first day—looking"),
    (r"psychology.\ufffd Eleanor", 'psychology." Eleanor'),
    (r"project.\ufffd Andy", 'project." Andy'),
    (r"project.\ufffd Andy Daly", 'project." Andy Daly'),
    (r"<strong>\ufffd a major", "<strong>— a major"),
    (r"Form pupils</strong> \ufffd a major", "Form pupils</strong> — a major"),
    (r"Cllr Simon Bywater: \ufffdA", 'Cllr Simon Bywater: "A'),
    (r"George \(16\): \ufffdIt", 'George (16): "It'),
    (r"Student George \(16\): \ufffdIt", 'Student George (16): "It'),
    (r"community\ufffd pupils can", "community— pupils can"),
    (r"environment.\ufffd</span>", 'environment."</span>'),
    (r"\ufffd", "–"),  # fallback: en dash for remaining prose
]


def repair(text: str) -> tuple[str, int]:
    count = text.count("\ufffd")
    if not count:
        return text, 0
    for pattern, replacement in RULES:
        text = re.sub(pattern, replacement, text)
    remaining = text.count("\ufffd")
    return text, count - remaining


def main() -> None:
    fixed_files = 0
    repaired_chars = 0
    for path in sorted(ROOT.rglob("*.html")):
        original = path.read_text(encoding="utf-8")
        if "\ufffd" not in original:
            continue
        updated, n = repair(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            fixed_files += 1
            repaired_chars += n
            leftover = updated.count("\ufffd")
            print(f"{path.relative_to(ROOT)}: repaired {n}, leftover {leftover}")
    print(f"Done. {fixed_files} files, {repaired_chars} replacements.")


if __name__ == "__main__":
    main()
