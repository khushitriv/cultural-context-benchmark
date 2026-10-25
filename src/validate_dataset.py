#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

VALID_STATUSES = {"draft", "needs_review", "validated", "excluded"}
VALID_TYPES = {"multiple_choice", "open_ended"}


def validate_item(item: object, line_number: int) -> list[str]:
    errors: list[str] = []
    prefix = f"line {line_number}"

    if not isinstance(item, dict):
        return [f"{prefix}: each JSONL line must contain a JSON object"]

    required = {
        "id", "version", "status", "primary_domain", "secondary_tags",
        "region", "community", "religion", "language", "question_type",
        "difficulty", "prompt", "options", "gold_answer", "acceptable_answers",
        "scoring_rubric", "explanation", "evidence", "known_variation",
        "author_review", "review_notes",
    }
    missing = required - item.keys()
    if missing:
        errors.append(f"{prefix} ({item.get('id', 'unknown')}): missing keys {sorted(missing)}")

    if item.get("status") not in VALID_STATUSES:
        errors.append(f"{prefix}: invalid status {item.get('status')!r}")
    qtype = item.get("question_type")
    if qtype not in VALID_TYPES:
        errors.append(f"{prefix}: invalid question_type {qtype!r}")

    prompt = item.get("prompt")
    if not isinstance(prompt, str) or len(prompt.strip()) < 10:
        errors.append(f"{prefix}: prompt must be a non-empty string")

    if not isinstance(item.get("difficulty"), int) or item.get("difficulty") not in (1, 2, 3):
        errors.append(f"{prefix}: difficulty must be integer 1, 2, or 3")

    options = item.get("options")
    if not isinstance(options, list):
        errors.append(f"{prefix}: options must be a list")
    elif qtype == "multiple_choice":
        ids = [o.get("id") for o in options if isinstance(o, dict)]
        if len(options) < 2:
            errors.append(f"{prefix}: multiple-choice items need at least two options")
        if len(ids) != len(options) or len(ids) != len(set(ids)):
            errors.append(f"{prefix}: each option must be an object with a unique id")
        if item.get("gold_answer") not in ids:
            errors.append(f"{prefix}: gold_answer must match one option id")
    elif qtype == "open_ended" and options:
        errors.append(f"{prefix}: open-ended items should have an empty options list")

    if item.get("status") == "validated":
        if item.get("author_review") != "reviewed":
            errors.append(f"{prefix}: validated item must have author_review='reviewed'")
        if not item.get("evidence"):
            errors.append(f"{prefix}: validated item must include at least one evidence record")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python src/validate_dataset.py path/to/questions.jsonl")
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR file not found {path}")
        return 2

    errors: list[str] = []
    seen_ids: set[str] = set()
    count = 0

    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            count += 1
            try:
                item = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc}")
                continue

            errors.extend(validate_item(item, line_number))
            if isinstance(item, dict):
                item_id = item.get("id")
                if isinstance(item_id, str):
                    if item_id in seen_ids:
                        errors.append(f"line {line_number}: duplicate id {item_id!r}")
                    seen_ids.add(item_id)

    if errors:
        print(f"FAILED--- {len(errors)} issue(s) across {count} item(s).")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS--- {count} item passed structural checks.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
