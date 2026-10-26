import importlib.util

import json
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1] / "reference" / "INDICA"

dataset_path = repo_root / "Dataset" / "dataset.json"
generator_path = (
    repo_root
    / "Experiments"
    / "CreateEvaluationQuestions"
    / "RAMCQ_creation.py"
)

spec = importlib.util.spec_from_file_location(
    "ramcq_creation", generator_path
)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

with dataset_path.open("r", encoding="utf-8") as f:
    questions = json.load(f)["questions"]

generated = []

for question in questions:
    mcq = generator.create_mcq_with_merged_duplicates(question)
    if mcq is not None:
        generated.append((question, mcq))

missing_category = sum(
    mcq.get("category") is None
    for _, mcq in generated
)

print("Generated mcq", len(generated))
print("Missing category", missing_category)
print("Category populated", len(generated) - missing_category)

restored = [
    (question, {**mcq, "category": question.get("question_domain")})
    for question, mcq in generated
]

restored_missing = sum(
    mcq.get("category") is None
    for _, mcq in restored
)

print("Missing category after domain mapping--", restored_missing)

for (_, original), (_, corrected) in zip(generated, restored):
    assert original["question_text"] == corrected["question_text"]
    assert original["options"] == corrected["options"]
    assert original["region_mapping"] == corrected["region_mapping"]

assert missing_category == len(generated)
assert restored_missing == 0

print("DONE \n domain mapping restores categories without changing mcq content")
