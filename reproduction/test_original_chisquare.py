
import importlib.util
import json
import tempfile
from pathlib import Path

from scipy.stats import chisquare


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    PROJECT_ROOT
    / "reference"
    / "INDICA"
    / "Experiments"
    / "Evaluation"
    / "ChiSquareTest.py"
)


def load_original_module():

    spec = importlib.util.spec_from_file_location(
        "original_chisquare", SCRIPT_PATH
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_jsonl(path, records):

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")


def synthetic_records():

    return [
        {
            "extracted_answer": "A",
            "parsed_answer": "A",
            "current_shuffled_mapping": str({
                "A": "North",
                "B": "South",
                "C": "East, West",
            }),
        },
        {
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


EXPECTED_REFERENCE = {
    "North": 0.5333333333,
    "South": 0.5333333333,
    "East": 0.3666666667,
    "West": 0.3666666667,
    "Central": 0.2,
}

OBSERVED_REFERENCE = {
    "North": 1.0,
    "South": 0.0,
    "East": 1.0,
    "West": 0.0,
    "Central": 0.0,
}


def assert_counts_close(actual, reference, tolerance=1e-6):

    for region, expected in reference.items():
        value = actual.get(region, 0.0)
        assert abs(value - expected) < tolerance, (
            f"{region}- expected {expected} got- {value}"
        )


def test_original_calculate_counts_matches_reference():

    module = load_original_module()

    with tempfile.TemporaryDirectory() as temp_dir:
        result_path = Path(temp_dir) / "synthetic_results.jsonl"
        write_jsonl(result_path, synthetic_records())

        counts = module.calculate_counts(str(result_path))

    assert_counts_close(counts["expected_counts"], EXPECTED_REFERENCE)
    assert_counts_close(counts["observed_counts"], OBSERVED_REFERENCE)


def test_invalid_response_does_not_change_counts():

    module = load_original_module()

    invalid_record = {
        "extracted_answer": "INVALID",
        "parsed_answer": None,
        "current_shuffled_mapping": str({
            "A": "North",
            "B": "South",
            "C": "East",
            "D": "West",
            "E": "Central",
        }),
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        baseline_path = Path(temp_dir) / "baseline.jsonl"
        invalid_path = Path(temp_dir) / "with_invalid.jsonl"

        records = synthetic_records()
        write_jsonl(baseline_path, records)
        write_jsonl(invalid_path, records + [invalid_record])

        baseline = module.calculate_counts(str(baseline_path))
        with_invalid = module.calculate_counts(str(invalid_path))

    for count_type in ("expected_counts", "observed_counts"):
        regions = (
            set(baseline[count_type])
            | set(with_invalid[count_type])
        )

        for region in regions:
            before = baseline[count_type].get(region, 0.0)
            after = with_invalid[count_type].get(region, 0.0)

            assert abs(before - after) < 1e-9, (
                f"{count_type} changed for {region}: "
                f"{before} -> {after}"
            )


def test_original_chi_square_matches_independent_calculation():

    module = load_original_module()

    with tempfile.TemporaryDirectory() as temp_dir:
        result_path = Path(temp_dir) / "synthetic_results.jsonl"
        write_jsonl(result_path, synthetic_records())

        counts = module.calculate_counts(str(result_path))
        original_result = module.perform_chi_square_test(
            str(result_path), "synthetic_test"
        )

    regions = ["North", "South", "East", "West", "Central"]

    observed = [
        counts["observed_counts"].get(region, 0.0)
        for region in regions
    ]
    expected = [
        counts["expected_counts"].get(region, 0.0)
        for region in regions
    ]

    independent_statistic, independent_p_value = chisquare(
        f_obs=observed,
        f_exp=expected,
    )

    assert original_result["status"] == "success"
    assert abs(
        original_result["chi_square_stat"] - independent_statistic
    ) < 1e-9
    assert abs(
        original_result["p_value"] - independent_p_value
    ) < 1e-9
    assert original_result["degrees_of_freedom"] == len(regions) - 1
