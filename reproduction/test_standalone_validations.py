import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPRODUCTION_DIR = PROJECT_ROOT / "reproduction"

VALIDATION_SCRIPTS = [
    "test_chisquare_reference_example.py",
    "test_chi_square.py",
    "test_fractional_attribution.py",
    "test_invalid_response_handling.py",
    "test_option_mapping.py",
    "test_paper_chi_square_example.py",
    "test_ramcq_metadata.py",
    "test_ramcq_metadata_impact.py",
    "test_result_filename_convention.py",
    "validate_dataset_generation.py",
]


@pytest.mark.parametrize("script_name", VALIDATION_SCRIPTS)
def test_standalone_validation_script(script_name):
    
    script_path = REPRODUCTION_DIR / script_name

    assert script_path.is_file(), f"Missing validation script: {script_path}"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )

    assert result.returncode == 0, (
        f"Validation script failed... {script_name}\n\n"
        f"STDOUT\n{result.stdout}\n\n"
        f"STDERR\n{result.stderr}"
    )
