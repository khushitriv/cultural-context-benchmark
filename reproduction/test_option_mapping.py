
import importlib.util
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EVAL_UTILS_PATH = (
    ROOT
    / "reference"
    / "INDICA"
    / "Experiments"
    / "Evaluation"
    / "eval_utils.py"
)

spec = importlib.util.spec_from_file_location(
    "eval_utils",
    EVAL_UTILS_PATH,
)

if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load {EVAL_UTILS_PATH}")

eval_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eval_utils)

create_ramcq_prompt = eval_utils.create_ramcq_prompt

question = {
    "question_text": "Which is a synthetic cultural practice example?",
    "options": {
        "A": "Answer shared by North",
        "B": "Answer shared by South and Central",
        "C": "Answer associated with East",
        "D": "Answer associated with West",
    },
    "region_mapping": {
        "A": ["North"],
        "B": ["South", "Central"],
        "C": ["East"],
        "D": ["West"],
    },
}

expected_regions = {
    "Answer shared by North": "North",
    "Answer shared by South and Central": "South, Central",
    "Answer associated with East": "East",
    "Answer associated with West": "West",
}

for seed in range(100):
    random.seed(seed)

    prompt, mapping = create_ramcq_prompt(
        question,
        shuffle_options=True,
    )

    displayed_options = re.findall(
        r"^([A-E])\. (.+)$",
        prompt,
        flags=re.MULTILINE,
    )

    assert len(displayed_options) == 4, (
        f"Seed {seed} expected four displayed options"
    )

    assert len(mapping) == 4, (
        f"Seed {seed} expected four mapping entries"
    )

    for letter, answer_text in displayed_options:
        assert answer_text in expected_regions, (
            f"Seed {seed} unexpected answer text {answer_text!r}"
        )

        assert mapping[letter] == expected_regions[answer_text], (
            f"Seed {seed} incorrect mapping for option {letter}"
        )

    shared_letter = next(
        letter
        for letter, answer_text in displayed_options
        if answer_text == "Answer shared by South and Central"
    )

    assert mapping[shared_letter] == "South, Central"

print("PASS--- 100 shuffles preserved all answerto region mappings")
print("PASS--- shared answer retained both associated regions")
