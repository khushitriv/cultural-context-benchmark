import json

import pytest

from analysis_runner import (
    analyze_directory,
    validate_result_file,
)


def test_validates_usable_and_skipped_records(tmp_path):
    path = tmp_path / "ModelA_RA_MCQ_results.jsonl"

    records = [
        {
            "extracted_answer": "A",
            "current_shuffled_mapping": {
                "A": "North",
                "B": "South",
            },
        },
        {
            "extracted_answer": None,
            "current_shuffled_mapping": "N/A",
        },
    ]

    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )

    assert validate_result_file(path) == {
        "total_records": 2,
        "usable_records": 1,
        "skipped_records": 1,
    }


def test_rejects_malformed_jsonl(tmp_path):
    path = tmp_path / "ModelA_RA_MCQ_results.jsonl"
    path.write_text("{not valid json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON"):
        validate_result_file(path)


def test_rejects_answer_not_in_mapping(tmp_path):
    path = tmp_path / "ModelA_RA_MCQ_results.jsonl"
    path.write_text(
        json.dumps({
            "extracted_answer": "Z",
            "current_shuffled_mapping": {"A": "North", "B": "South"},
        }) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="not a key"):
        validate_result_file(path)


def test_synthetic_result_runs_through_analysis(tmp_path):
    path = tmp_path / "Synthetic_RA_MCQ_results.jsonl"

    # two synthetic runs matching the papers reference example
    records = [
        {
            "extracted_answer": "A",
            "current_shuffled_mapping": {
                "A": "North",
                "B": "South",
                "C": "East, West",
            },
        },
        {
            "extracted_answer": "C",
            "current_shuffled_mapping": {
                "A": "North",
                "B": "South",
                "C": "East",
                "D": "West",
                "E": "Central",
            },
        },
    ]

    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )

    summaries = analyze_directory(tmp_path)

    assert len(summaries) == 1
    assert summaries[0]["model"] == "Synthetic"
    assert summaries[0]["usable_records"] == 2

    result = summaries[0]["analysis_result"]
    assert isinstance(result, dict)