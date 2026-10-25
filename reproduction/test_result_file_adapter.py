import pytest

from result_file_adapter import (
    discover_result_files,
    extract_model_name,
)


def test_discovers_ra_mcq_results(tmp_path):
    result_file = tmp_path / "ModelA_RA_MCQ_results.jsonl"
    result_file.write_text('{"test": true}\n', encoding="utf-8")

    discovered = discover_result_files(tmp_path)

    assert discovered == [result_file]
    assert extract_model_name(discovered[0]) == "ModelA"


def test_discovers_legacy_adversarial_mcq_results(tmp_path):
    result_file = tmp_path / "ModelB_ADVERSARIAL_MCQ_results.jsonl"
    result_file.write_text('{"test": true}\n', encoding="utf-8")

    discovered = discover_result_files(tmp_path)

    assert discovered == [result_file]
    assert extract_model_name(discovered[0]) == "ModelB"


def test_discovers_both_conventions_without_duplicates(tmp_path):
    ra_file = tmp_path / "ModelA_RA_MCQ_results.jsonl"
    legacy_file = tmp_path / "ModelB_ADVERSARIAL_MCQ_results.jsonl"

    ra_file.write_text('{"test": true}\n', encoding="utf-8")
    legacy_file.write_text('{"test": true}\n', encoding="utf-8")

    discovered = discover_result_files(tmp_path)

    assert discovered == sorted([ra_file, legacy_file])
    assert {extract_model_name(path) for path in discovered} == {
        "ModelA",
        "ModelB",
    }


def test_rejects_unrecognized_filename():
    with pytest.raises(ValueError, match="Unrecognized result filename"):
        extract_model_name("ModelC_RASA_results.jsonl")


def test_empty_directory_returns_no_files(tmp_path):
    assert discover_result_files(tmp_path) == []