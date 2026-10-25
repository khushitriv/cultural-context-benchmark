
import importlib.util
import json
import tempfile
from pathlib import Path

script = (
    Path(__file__).resolve().parents[1]
    / "reference"
    / "INDICA"
    / "Experiments"
    / "Evaluation"
    / "ChiSquareTest.py"
)

spec = importlib.util.spec_from_file_location("chi_square", script)
chi_square = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chi_square)

mapping = {
    "A": "North",
    "B": "South",
    "C": "East",
    "D": "West",
    "E": "Central",
}

results = [
    {
        "question_id": "synthetic_chi_test",
        "extracted_answer": "A",
        "parsed_answer": "A",
        "current_shuffled_mapping": str(mapping),
    },
    {
        "question_id": "synthetic_chi_test",
        "extracted_answer": None,
        "parsed_answer": None,
        "current_shuffled_mapping": str(mapping),
    },
]

with tempfile.TemporaryDirectory() as tmp:
    results_path = Path(tmp) / "synthetic_results.jsonl"
    results_path.write_text(
        "".join(json.dumps(row) + "\n" for row in results),
        encoding="utf-8",
    )

    counts = chi_square.calculate_counts(str(results_path))
    print("counts expected-", counts["expected_counts"])
    print("counts Observed -", counts["observed_counts"])

    assert abs(sum(counts["expected_counts"].values()) - 1.0) < 1e-9
    assert abs(counts["observed_counts"]["North"] - 1.0) < 1e-9
    assert all(
        abs(counts["expected_counts"][r] - 0.2) < 1e-9
        for r in ["North", "South", "East", "West", "Central"]
    )

    print("PASS")

    result = chi_square.perform_chi_square_test(
        str(results_path),
        "SyntheticTest",
    )
    print("Chi-square result:", result)
