
import json
from pathlib import Path

from ramcq_metadata_fix import (
    create_mcq_with_corrected_metadata,
    load_original_generator,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = (
    PROJECT_ROOT / "reference" / "INDICA" / "Dataset" / "dataset.json"
)


def test_corrected_metadata_matches_source_domain():
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)

    original_generator = load_original_generator()

    for question in dataset["questions"]:
        original = original_generator.create_mcq_with_merged_duplicates(
            question
        )
        corrected = create_mcq_with_corrected_metadata(question)

        if original is None:
            assert corrected is None
            continue

        assert corrected["category"] == question["question_domain"]
        assert corrected["question_text"] == original["question_text"]
        assert corrected["options"] == original["options"]
        assert corrected["region_mapping"] == original["region_mapping"]
        assert corrected["test_type"] == original["test_type"]



def test_adapter_does_not_invent_missing_domains(monkeypatch):
    import ramcq_metadata_fix

    def fake_generator_function(data, min_options=3):
        return {
            "question_text": data["question_text"],
            "options": ["A", "B", "C"],
            "region_mapping": {},
            "test_type": "complete",
            "category": "incorrect-placeholder",
        }

    class FakeGenerator:
        create_mcq_with_merged_duplicates = staticmethod(
            fake_generator_function
        )

    monkeypatch.setattr(
        ramcq_metadata_fix,
        "load_original_generator",
        lambda: FakeGenerator,
    )

    question = {
        "question_id": "synthetic-no-domain",
        "question_text": "Synthetic test question",
    }

    corrected = ramcq_metadata_fix.create_mcq_with_corrected_metadata(
        question
    )

    assert corrected is not None
    assert corrected["category"] is None