
import json
from pathlib import Path

repo_root = Path("reference/INDICA")
dataset_path = repo_root / "Dataset" / "dataset.json"
generator_path = (
    repo_root
    / "Experiments"
    / "CreateEvaluationQuestions"
    / "RAMCQ_creation.py"
)

with dataset_path.open("r", encoding="utf-8") as f:
    dataset = json.load(f)

questions = dataset["questions"]

print("Source dataset:-")
print("Questions:-", len(questions))
print("Has question_domain:-", "question_domain" in questions[0])
print("Has question_category:-", "question_category" in questions[0])

source_domains = sum(
    bool(q.get("question_domain")) for q in questions
)
source_categories = sum(
    bool(q.get("question_category")) for q in questions
)

print("Questions with question_domain:-", source_domains)
print("Questions with question_category:-", source_categories)

generator_source = generator_path.read_text(encoding="utf-8")

print("\nGenerator source")
print(
    'Reads question_category:-',
    'data.get("question_category")' in generator_source,
)
print(
    'teads question_domain:-',
    'data.get("question_domain")' in generator_source,
)

assert source_domains > 0, "Expected source domain labels."
assert source_categories == 0, (
    "the source schema differs from the schema assumed by this test"
)
assert 'data.get("question_category")' in generator_source

print("The source and generator use different metadata keys \n OK")
