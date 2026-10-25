
import importlib.util
import json
import tempfile
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "reference"
    / "INDICA"
    / "Experiments"
    / "Evaluation"
    / "RAMCQ_bias_detection.py"
)

spec = importlib.util.spec_from_file_location("bias_detection", SCRIPT)
bias_detection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bias_detection)

mcq = {
    "question_id": "synthetic_invalid_test",
    "question_text": "Synthetic test question?",
    "category": "Test",
    "subcategory": "Test",
    "topic": "Test",
    "options": {
        "A": "Answer from North",
        "B": "Answer from South",
        "C": "Answer from East",
        "D": "Answer from West",
        "E": "Answer from Central",
    },
    "region_mapping": {
        "A": ["North"],
        "B": ["South"],
        "C": ["East"],
        "D": ["West"],
        "E": ["Central"],
    },
}

results = [
    {
        "question_id": "synthetic_invalid_test",
        "run_number": 1,
        "extracted_answer": "A",
        "parsed_answer": "A",
        "current_shuffled_mapping": str({
            "A": "North",
            "B": "South",
            "C": "East",
            "D": "West",
            "E": "Central",
        }),
    },
    {
        "question_id": "synthetic_invalid_test",
        "run_number": 2,
        "extracted_answer": None,
        "parsed_answer": None,
        "current_shuffled_mapping": str({
            "A": "North",
            "B": "South",
            "C": "East",
            "D": "West",
            "E": "Central",
        }),
    },
]

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    mcq_path = tmp / "mcq_questions.json"
    results_path = tmp / "synthetic_results.jsonl"

    mcq_path.write_text(
        json.dumps({"questions": [mcq]}),
        encoding="utf-8",
    )
    results_path.write_text(
        "".join(json.dumps(row) + "\n" for row in results),
        encoding="utf-8",
    )

    report = bias_detection.calculate_bias_simple(
        str(mcq_path),
        str(results_path),
        model_name="SyntheticTest",
    )

    print(json.dumps(report, indent=2, default=str))
