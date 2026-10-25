
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ANALYSIS_PATH = (
    ROOT
    / "reference"
    / "INDICA"
    / "Experiments"
    / "Evaluation"
    / "RAMCQ_bias_detection.py"
)

spec = importlib.util.spec_from_file_location(
    "ramcq_bias_detection",
    ANALYSIS_PATH,
)

if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load {ANALYSIS_PATH}")

analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)

mcq_data = {
    "questions": [
        {
            "question_id": "synthetic_001",
            "question_text": "Synthetic test question",
            "category": "Synthetic",
            "subcategory": "Test",
            "topic": "Attribution",
            "options": {
                "A": "North answer",
                "B": "Shared answer",
                "C": "East answer",
                "D": "West answer",
            },
            "region_mapping": {
                "A": ["North"],
                "B": ["South", "Central"],
                "C": ["East"],
                "D": ["West"],
            },
        }
    ]
}

mapping = {
    "A": "North",
    "B": "South, Central",
    "C": "East",
    "D": "West",
}

results = [
    {
        "question_id": "synthetic_001",
        "run_number": 1,
        "extracted_answer": "B",
        "current_shuffled_mapping": str(mapping),
    },
    {
        "question_id": "synthetic_001",
        "run_number": 2,
        "extracted_answer": "A",
        "current_shuffled_mapping": str(mapping),
    },
]

with tempfile.TemporaryDirectory() as temp_dir:
    temp = Path(temp_dir)
    mcq_path = temp / "synthetic_mcqs.json"
    results_path = temp / "synthetic_results.jsonl"

    mcq_path.write_text(
        json.dumps(mcq_data),
        encoding="utf-8",
    )

    results_path.write_text(
        "\n".join(json.dumps(row) for row in results) + "\n",
        encoding="utf-8",
    )

    output = analysis.calculate_bias_simple(
        str(mcq_path),
        str(results_path),
        model_name="SyntheticTest",
    )

rates = output["overall_bias"]


for region in ["North", "South", "East", "West", "Central"]:
    assert rates[region]["times_available"] == 2, (
        f"Unexpected availability for {region}"
    )


assert rates["North"]["times_selected"] == 1.0
assert rates["South"]["times_selected"] == 0.5
assert rates["Central"]["times_selected"] == 0.5


assert rates["North"]["selection_rate"] == 0.5
assert rates["South"]["selection_rate"] == 0.25
assert rates["Central"]["selection_rate"] == 0.25


assert output["total_responses_processed"] == 2
assert output["total_responses_skipped"] == 0

print("PASS")

print("\nexpected regional results")
for region in ["North", "South", "East", "West", "Central"]:
    row = rates[region]
    print(
        f"{region:8} "
        f"selected={row['times_selected']:.1f}, "
        f"available={row['times_available']}, "
        f"rate={row['selection_rate']:.2f}"
    )
