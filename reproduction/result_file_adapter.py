from pathlib import Path
import glob


def discover_result_files(results_dir):

    results_dir = Path(results_dir)

    patterns = (
        "*_RA_MCQ_results.jsonl",
        "*_ADVERSARIAL_MCQ_results.jsonl",
    )

    found = set()

    for pattern in patterns:
        found.update(
            Path(path)
            for path in glob.glob(str(results_dir / pattern))
        )

    return sorted(found)


def extract_model_name(result_file):
    
    stem = Path(result_file).stem

    suffixes = (
        "_RA_MCQ_results",
        "_ADVERSARIAL_MCQ_results",
    )

    for suffix in suffixes:
        if stem.endswith(suffix):
            return stem[:-len(suffix)]

    raise ValueError(
        f"Unrecognized result filename convention: {Path(result_file).name}"
    )