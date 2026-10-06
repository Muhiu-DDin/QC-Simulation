"""Stored answer interface. This file never calls the calculation engine.

Edit data/chapter10_answers.json to add a teacher-provided answer, retaining
its provenance, page and tolerance. Do not regenerate references from solver output.
"""
import json
from pathlib import Path
ANSWER_FILE=Path(__file__).resolve().parent/'data/chapter10_answers.json'
def load_answers(path=ANSWER_FILE):
    return json.loads(Path(path).read_text(encoding='utf-8'))['references']
