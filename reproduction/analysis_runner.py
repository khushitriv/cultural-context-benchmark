import ast
import importlib.util
import json
from pathlib import Path

from result_file_adapter import (
    discover_result_files,
    extract_model_name,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHI_SQUARE_SCRIPT = (
    PROJECT_ROOT
    / "reference"
    / "INDICA"
    / "Experiments"
    / "Evaluation"
    / "ChiSquareTest.py"
)


def load_reference_analysis():
    
    spec = importlib.util.spec_from_file_location(
        "indica_chi_square_original",
        CHI_SQUARE_SCRIPT,
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load analysis script {CHI_SQUARE_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_result_file(path):

    total = 0
    usable = 0
    skipped = 0

    with Path(path).open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            total += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}, line {line_number} invalid json {exc}"
                ) from exc

            if not isinstance(record, dict):
                raise ValueError(
                    f"{path}, line {line_number} expected a JSON object"
                )

            answer = (
                record.get("extracted_answer")
                or record.get("parsed_answer")
            )
            mapping = record.get("current_shuffled_mapping")

            
            if not answer or not mapping or mapping == "N/A":
                skipped += 1
                continue

            if isinstance(mapping, str):
                try:
                    mapping = ast.literal_eval(mapping)
                except (ValueError, SyntaxError) as exc:
                    raise ValueError(
                        f"{path}, line {line_number}-- mapping is not "
                        "a valid Python literal dictionary"
                    ) from exc

            if not isinstance(mapping, dict):
                raise ValueError(
                    f"{path}, line {line_number} mapping must be a dictionary.."
                )

            if answer not in mapping:
                raise ValueError(
                    f"{path}, line {line_number}-- selected answer "
                    "is not a key in the mapping.."
                )

            if not isinstance(mapping[answer], str):
                raise ValueError(
                    f"{path}, line {line_number} selected mapping value "
                    "must be a region string..!"
                )

            usable += 1

    return {
        "total_records": total,
        "usable_records": usable,
        "skipped_records": skipped,
    }


def analyze_directory(results_dir):
    analysis = load_reference_analysis()
    result_files = discover_result_files(results_dir)

    if not result_files:
        print(f"no matching result files found in {results_dir}")
        return []

    summaries = []

    for path in result_files:
        model_name = extract_model_name(path)

        counts = validate_result_file(path)

        if counts["usable_records"] == 0:
            print(f"\nSKIP {path.name} for no usable records")
            continue

        result = analysis.perform_chi_square_test(
            str(path),
            model_name,
        )

        summaries.append({
            "file": path.name,
            "model": model_name,
            **counts,
            "analysis_result": result,
        })

        print(f"\nProcessed:- {path.name}")
        print(f"Model:- {model_name}")
        print(f"Records:- {counts['total_records']}")
        print(f"Usable:- {counts['usable_records']}")
        print(f"Skipped:- {counts['skipped_records']}")
        print(json.dumps(result, indent=2, default=str))

    return summaries


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate and analyze INDICA MCQ result files..."
    )
    parser.add_argument(
        "results_dir",
        help="Directory containing result JSONL files..",
    )
    args = parser.parse_args()

    analyze_directory(args.results_dir)