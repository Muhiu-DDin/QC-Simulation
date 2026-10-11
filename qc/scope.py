"""The assigned Chapter 10 exercises, without modifying the source catalogue.

The book uses identifiers such as ``10-40``; a letter identifies a numerical
subpart. Conceptual questions are documented in the assignment manifest and are
not turned into invented numerical inputs.
"""

import json
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "chapter10_inputs.json"
MANIFEST_FILE = ROOT / "data" / "assignment_scope.json"
FIRST_EXERCISE = 40
LAST_EXERCISE = 59
ASSIGNMENT_LABEL = "Chapter 10: Exercises 10.40-10.59"
_CASE_ID = re.compile(r"^10-(\d+)([a-z]*)$")


def in_assignment(case_id):
    """Whether a regular exercise identifier falls within the assigned range."""
    match = _CASE_ID.fullmatch(case_id) if isinstance(case_id, str) else None
    return bool(match and FIRST_EXERCISE <= int(match.group(1)) <= LAST_EXERCISE)


def assigned_cases(cases=None):
    """Return numerical cases 10.40-10.59 in book order.

    With no argument, read the preserved full catalogue. An iterable of cases
    can also be supplied by callers that have already loaded that catalogue.
    The returned case dictionaries retain their original IDs and input data.
    """
    if cases is None:
        cases = json.loads(INPUT_FILE.read_text(encoding="utf-8"))["cases"]
    selected = [case for case in cases if in_assignment(case.get("id"))]
    return sorted(
        selected,
        key=lambda case: (
            int(_CASE_ID.fullmatch(case["id"]).group(1)),
            _CASE_ID.fullmatch(case["id"]).group(2),
        ),
    )


def assignment_manifest():
    """Return the coverage map, including qualitative questions without data."""
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


def calculation_fingerprint():
    """Identify the formula/model sources used to generate a saved book run."""
    files = ("calculations.py", "simulation.py", "comparison.py")
    return hashlib.sha256(b"\0".join((ROOT / "qc" / name).read_bytes() for name in files)).hexdigest()
