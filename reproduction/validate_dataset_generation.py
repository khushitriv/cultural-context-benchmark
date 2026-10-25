
import importlib.util
import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "reference"
    / "INDICA"
    / "Dataset"
    / "dataset.json"
)

GENERATOR_PATH = (
    PROJECT_ROOT
    / "reference"
    / "INDICA"
    / "Experiments"
    / "CreateEvaluationQuestions"
    / "RAMCQ_creation.py"
)


def load_generator():
    
    spec = importlib.util.spec_from_file_location(
        "ramcq_creation",
        GENERATOR_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the RA-MCQ generator...")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():

    for path in (DATASET_PATH, GENERATOR_PATH):
        if not path.exists():
            raise FileNotFoundError(f"file not found {path}")

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    questions = dataset["questions"]
    generator = load_generator()

    mcqs = []

    for question in questions:
        mcq = generator.create_mcq_with_merged_duplicates(question)

        if mcq is not None:
            mcqs.append(mcq)

    test_types = Counter(q["test_type"] for q in mcqs)
    option_counts = Counter(q["num_options"] for q in mcqs)

    shared_questions = sum(
        bool(q["shared_answers"]) for q in mcqs
    )

    missing_categories = sum(
        q.get("category") is None for q in mcqs
    )

    print("\n RA-MCQ Dataset Validation ")
    print(f"Source questions:- {len(questions)}")
    print(f"Generated MCQs:- {len(mcqs)}")
    print(f"Complete questions:- {test_types['complete']}")
    print(f"Partial questions:- {test_types['partial']}")
    print(f"Option counts:- {dict(sorted(option_counts.items()))}")
    print(f"Questions with shared answers: {shared_questions}")
    print(f"MCQs missing category metadata:- {missing_categories}")

    assert len(questions) == 515, "unexpected source dataset size"
    assert len(mcqs) == 79, "Generated MCQ count differs from audit"
    assert test_types["complete"] == 32
    assert test_types["partial"] == 47
    assert dict(option_counts) == {3: 47, 4: 22, 5: 10}

    print("dataset generation counts matches audit")

    if missing_categories:
        print(
            "some generated MCQs could lack category metadata "
            "Inspect the source field names before correcting the generator"
        )


if __name__ == "__main__":
    main()
