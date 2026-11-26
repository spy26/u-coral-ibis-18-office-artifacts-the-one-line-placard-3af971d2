"""Placard writer for "Office Artifacts: The One-Line Placard Contest".

The program emits one line: a museum placard for an ordinary office
keyboard, written as if the keyboard were an ancient artifact dug from a
lost civilisation. It validates the line against the competition gate
(one line, 1-180 characters, not only whitespace), writes it to
``entry.txt`` in the make.fun output directory, and proves every write by
reading the file back and comparing the exact bytes.

Deterministic by design: no files are read, no network is opened, no clock
is consulted and no randomness is used. The text below is a fixed literal;
running the program twice always produces the same bytes.
"""

import os
import re
import sys
from pathlib import Path

TEXT = (
    "Keyboard, c. 2015, ABS plastic, its spacebar worn smooth by a thousand "
    "unsent resignations; the 'Esc' key never worked. "
    "Found in a drawer, unclaimed."
)

MIN_CHARS = 1
MAX_CHARS = 180
FILENAME = "entry.txt"
DEFAULT_OUTPUT = Path("/output")
# A museum placard needs a catalogue date ("c. YYYY"); without one the
# line is a joke about an office, not a placard for an artifact.
DATE_PATTERN = re.compile(r"\bc\.\s*\d{4}\b")


class GateFailure(Exception):
    """The placard or a write failed the competition gate."""


def check(text):
    """Return a list of gate violations; an empty list means the text passes."""
    violations = []
    if len(text) < MIN_CHARS:
        violations.append("empty: placard has 0 characters (minimum 1)")
    if len(text) > MAX_CHARS:
        violations.append(
            "too long: placard has %d characters (maximum %d)"
            % (len(text), MAX_CHARS)
        )
    if text.strip() == "":
        violations.append("blank: placard is only whitespace")
    if "\n" in text or "\r" in text:
        violations.append("multi-line: placard contains a line break")
    if text != text.strip():
        violations.append("padding: placard has leading or trailing whitespace")
    if "  " in text:
        violations.append("spacing: placard contains a double space")
    bad = [ch for ch in text if ord(ch) < 32 or ord(ch) == 127]
    if bad:
        violations.append(
            "control characters: placard contains %d control character(s)" % len(bad)
        )
    if not DATE_PATTERN.search(text):
        violations.append(
            "no catalogue date: placard has no 'c. YYYY' date, "
            "so it is not a museum placard"
        )
    return violations


def store(folder, payload):
    """Write payload to folder/entry.txt, then prove it by reading it back."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / FILENAME
    path.write_bytes(payload)
    actual = path.read_bytes()
    if actual != payload:
        raise GateFailure(
            "read-back mismatch in %s: wrote %d bytes, read %d bytes"
            % (path, len(payload), len(actual))
        )
    return path


def main():
    """Validate the placard, store it, and report the result."""
    problems = check(TEXT)
    if problems:
        for problem in problems:
            print("INVALID: " + problem, file=sys.stderr)
        return 1

    payload = TEXT.encode("utf-8")
    print(TEXT)

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT)
    targets = [out_dir]
    if out_dir.resolve() != DEFAULT_OUTPUT.resolve():
        targets.append(DEFAULT_OUTPUT)

    for folder in targets:
        written = store(folder, payload)
        print("wrote %s (%d bytes)" % (written, len(payload)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
