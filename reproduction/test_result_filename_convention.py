
from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference" / "INDICA" / "Experiments" / "Evaluation"

driver_path = REFERENCE / "evaluate_all_models.py"
logger_path = REFERENCE / "results_logger.py"
chi_path = REFERENCE / "ChiSquareTest.py"

driver = driver_path.read_text(encoding="utf-8")
logger = logger_path.read_text(encoding="utf-8")
chi_square = chi_path.read_text(encoding="utf-8")

assert '"RA_MCQ"' in driver, "RA_MCQ category not found in evaluation driver."

# verifying how the logger makes the output filenames
assert "f\"{safe_model_name}_{safe_category}_results.jsonl\"" in logger, (
    "Expected jsonl filename pattern not found in results_logger.py."
)

# extracting the filename glob used by the chi-square script
match = re.search(
    r'glob\.glob\(os\.path\.join\(results_dir,\s*"([^"]+)"\)\)',
    chi_square,
)
assert match, "Could not identify the result-file glob in ChiSquareTest.py."
chi_glob = match.group(1)

logger_pattern = "MODEL_RA_MCQ_results.jsonl"
chi_matches_standard_output = (
    re.fullmatch(chi_glob.replace("*", ".*"), logger_pattern) is not None
)

print("Evaluation category: RA_MCQ")
print("Logger example:     ", logger_pattern)
print("Chi-square glob:    ", chi_glob)
print("Standard output matched by chi-square glob:",
      chi_matches_standard_output)

assert not chi_matches_standard_output, (
    "The filename mismatch no longer reproduces inspect the source further"
)

print("\nfilename mismatch present")
