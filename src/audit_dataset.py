
import json
from collections import Counter
from pathlib import Path

DATASET_PATH = Path("data/draft/questions.jsonl")


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found {DATASET_PATH}. "
            
        )

    questions = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                question = json.loads(line)
            except json.JSONDecodeError as error:
                print(f"jsonfile error on line {line_number}: {error}")
                continue

            question["_line_number"] = line_number
            questions.append(question)

   
    print("CULTURAL-CONTEXT BENCHMARK--- DATASET AUDIT")
   
    print(f"Total questions- {len(questions)}")

    # 1 Check the question ID
    ids = [q.get("id") for q in questions]
    id_counts = Counter(ids)
    duplicate_ids = [
        question_id
        for question_id, count in id_counts.items()
        if count > 1
    ]

    print("ID CHECK")
    print(f"Unique ID- {len(set(ids))}")
    print(f"Duplicate ID- {duplicate_ids or 'None'}")

    print("QUESTION DISTRIBUTION")
    print("Types-", dict(Counter(
        q.get("question_type", "MISSING")
        for q in questions
    )))
    print("Domains-", dict(Counter(
        q.get("primary_domain", q.get("domain", "MISSING"))
        for q in questions
    )))
    print("Statuses", dict(Counter(
        q.get("status", "MISSING")
        for q in questions
    )))

    # missing or incomplete evidence
    print("EVIDENCE COVERAGE")
    missing_evidence = []

    for q in questions:
        evidence = q.get("evidence", [])

        if not evidence:
            missing_evidence.append(q.get("id", "UNKNOWN"))
            continue

        for source in evidence:
            if not source.get("citation") or not source.get("url"):
                print(
                    f"INCOMPLETE SOURCE: {q.get('id')} "
                    "(citation or URL missing)"
                )

    print(f"Questions with no evidence: {len(missing_evidence)}")
    for question_id in missing_evidence:
        print(f"  - {question_id}")

    # checking whether items have basic scoring information
    print("ANSWER AND SCORING CHECK")
    incomplete_scoring = []

    for q in questions:
        problems = []

        if not q.get("prompt"):
            problems.append("missing prompt")

        if q.get("gold_answer") in (None, ""):
            problems.append("missing gold_answer")

        if not q.get("scoring_rubric"):
            problems.append("missing scoring_rubric")

        question_type = q.get("question_type")
        options = q.get("options", [])
        answer = q.get("gold_answer")

        if question_type == "multiple_choice":
            option_ids = {
                option.get("id")
                for option in options
                if isinstance(option, dict)
            }

            if len(option_ids) < 2:
                problems.append("fewer than two valid options")

            if answer not in option_ids:
                problems.append(
                    "gold_answer does not match an option ID"
                )

        elif question_type == "open_ended":
            if options:
                problems.append(
                    "open-ended item unexpectedly has options"
                )

        else:
            problems.append("unknown or missing question_type")

        if problems:
            incomplete_scoring.append((q.get("id"), problems))

    if incomplete_scoring:
        for question_id, problems in incomplete_scoring:
            print(f"Checking {question_id}: {', '.join(problems)}")
    else:
        print("No basic answer or scoring issues found...")

    # show thw items that still need human review
    print("STATUS REVIEW")
    needs_review = [
        q.get("id", "UNKNOWN")
        for q in questions
        if q.get("status") != "validated"
        or q.get("author_review") != "approved"
    ]

    print(f"Items not fully approved- {len(needs_review)}")

    print("AUDIT COMPLETE!!!")


if __name__ == "__main__":
    main()
