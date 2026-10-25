
from pathlib import Path
import importlib.util

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ORIGINAL_GENERATOR = (
    PROJECT_ROOT
    / "reference"
    / "INDICA"
    / "Experiments"
    / "CreateEvaluationQuestions"
    / "RAMCQ_creation.py"
)


def load_original_generator():
    spec = importlib.util.spec_from_file_location(
        "indica_ramcq_original_generator",
        ORIGINAL_GENERATOR,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load generatpr {ORIGINAL_GENERATOR}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_mcq_with_corrected_metadata(data, min_options=3):
    generator = load_original_generator()
    mcq = generator.create_mcq_with_merged_duplicates(
        data, min_options=min_options
    )

    if mcq is not None:
        mcq["category"] = data.get("question_domain")

    return mcq
