
import csv
import json
from pathlib import Path

INPUT_PATH = Path("data/draft/questions.jsonl")
OUTPUT_PATH = Path("data/review/question_review_sheet.csv")

QUESTION_FIELDS = [
    "id", "version", "primary_domain", "secondary_tags",
    "region", "community", "religion", "language",
    "question_type", "difficulty", "prompt", "options",
    "gold_answer", "acceptable_answers", "scoring_rubric",
    "explanation", "evidence", "known_variation", "status",
    "author_review", "review_notes",
]

REVIEW_FIELDS = [
    "source_status", "source_supports_claim", "scope_accurate",
    "answer_key_defensible", "ambiguity_check", "overlap_check",
    "recommended_action", "reviewer_notes",
]


def serialize(value):
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found {INPUT_PATH}. "
        )

    questions = []

    with INPUT_PATH.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                questions.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"invalid Json on line {line_number}: {error}"
                ) from error

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=QUESTION_FIELDS + REVIEW_FIELDS
        )
        writer.writeheader()

        for question in questions:
            row = {
                field: serialize(question.get(field))
                for field in QUESTION_FIELDS
            }
            row.update({field: "" for field in REVIEW_FIELDS})
            writer.writerow(row)

    print(f"Exported {len(questions)} questions.")
    print(f"Created-- {OUTPUT_PATH.resolve()}")
    print("Original jsonl wasnt modified")


if __name__ == "__main__":
    main()
