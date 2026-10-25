
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

results = [
    {
        "question_id": "paper_example_1",
        "extracted_answer": "A",
        "parsed_answer": "A",
        "current_shuffled_mapping": str({
            "A": "North",
            "B": "South",
            "C": "East, West",
        }),
    },
    {
        "question_id": "paper_example_2",
        "extracted_answer": "C",
        "parsed_answer": "C",
        "current_shuffled_mapping": str({
            "A": "North",
            "B": "South",
            "C": "East",
            "D": "West",
            "E": "Central",
        }),
    },
]

expected_paper = {
    "North": 0.5333333333333333,
    "South": 0.5333333333333333,
    "East": 0.3666666666666667,
    "West": 0.3666666666666667,
    "Central": 0.2,
}

observed_paper = {
    "North": 1.0,
    "South": 0.0,
    "East": 1.0,
    "West": 0.0,
    "Central": 0.0,
}

with tempfile.TemporaryDirectory() as tmp:
    results_path = Path(tmp) / "paper_example.jsonl"
    results_path.write_text(
        "".join(json.dumps(row) + "\n" for row in results),
        encoding="utf-8",
    )

    counts = chi_square.calculate_counts(str(results_path))
    expected = counts["expected_counts"]
    observed = counts["observed_counts"]

    for region, value in expected_paper.items():
        assert abs(expected[region] - value) < 1e-9, (
            f"{region}: expected {value}, got {expected[region]}"
        )

    for region, value in observed_paper.items():
        assert abs(observed.get(region, 0.0) - value) < 1e-9, (
            f"{region}: expected {value}, got {observed.get(region, 0.0)}"
        )

    print("OK expected regional counts match the papers worked example!!")
    print("observed regional counts match the paper worked example")

    result = chi_square.perform_chi_square_test(
        str(results_path),
        "PaperExample",
    )
    print(json.dumps(result, indent=2))
