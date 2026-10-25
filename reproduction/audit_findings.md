# INDICA Reproduction — Code Audit and Validation Report

## 1. Project scope

This project audits and validates selected components of the INDICA paper's code and data pipeline while preserving the original reference repository.

The work focuses on dataset generation, metadata integrity, chi-square calculations, result-file discovery, and synthetic integration testing.

**Scope limitation:** This is a partial code-level reproduction and audit, not a complete reproduction of the paper's model experiments. No paid model API calls are used.

## 2. Finding 1 — RA-MCQ result filename mismatch

**Status:** Confirmed by source inspection and static test  
**Severity:** High for pipeline integration; does not establish a statistical-method error.

### Evidence

- `Experiments/Evaluation/evaluate_all_models.py` uses the `RA_MCQ` evaluation category.
- `Experiments/Evaluation/results_logger.py` incorporates the evaluation category into result filenames, producing names such as `MODEL_RA_MCQ_results.jsonl`.
- `Experiments/Evaluation/ChiSquareTest.py` searches for files matching `*_ADVERSARIAL_MCQ_results.jsonl`.
- The standard RA-MCQ filename convention does not match the chi-square script's search pattern.

### Consequence

Results generated using the standard RA-MCQ naming convention will not be discovered by the original chi-square script's configured glob. Another workflow may produce files with the expected suffix, but its existence and experimental equivalence have not been established.

### Verification

The reproduction-side test `test_result_filename_convention.py` confirms that the standard logger filename does not match the original chi-square glob. No model API calls were made.

The reproduction-side `result_file_adapter.py` discovers both filename conventions without renaming files. Its behavior is covered by `test_result_file_adapter.py`.

### Recommended handling

Preserve the upstream implementation and document the mismatch. Use the reproduction-side adapter for controlled analysis, subject to validation of each file's schema and experimental provenance. Do not assume that `RA_MCQ` and `ADVERSARIAL_MCQ` are interchangeable experiment categories.

## 3. Finding 2 — RAMCQ category metadata mismatch

**Status:** Confirmed by source inspection and tests  
**Impact:** Generated category metadata and downstream category-level reporting.

### Evidence

- The source dataset uses the field `question_domain`.
- `Experiments/CreateEvaluationQuestions/RAMCQ_creation.py` reads `question_category` when populating the generated MCQ's `category` field.
- The source dataset does not contain `question_category`, so the original generation path produces missing category values for the generated MCQs.
- The reproduction-side `ramcq_metadata_fix.py` maps `question_domain` to `category`.

### Consequence

Category-level aggregation and reporting may be incomplete or incorrect when generated MCQs lack their intended category metadata. This finding does not, by itself, establish that the overall regional selection calculations are incorrect.

### Verification

- `test_ramcq_metadata.py` checks the mismatch between source and generator field names.
- `test_ramcq_metadata_fix.py` checks that the reproduction-side adapter restores category metadata while preserving the tested MCQ content.

### Recommended handling

Keep the upstream generator unchanged. Apply the correction only in the separately maintained reproduction workflow, and explicitly document it as a deviation from the original implementation.

## 4. Dataset and generation validation

The local dataset-generation audit reports:

| Check | Result |
|---|---:|
| Source questions | 515 |
| Generated RAMCQ MCQs | 79 |
| Regional QA pairs | 1,630 |

The generated MCQ count is consistent with the domain counts reported in the paper's appendix. The regional QA pair count also matches the paper's reported figure.

These checks establish agreement on the audited counts. They do not prove that every generated item, prompt, or downstream model response reproduces the original experiment exactly.

## 5. Statistical calculation validation

**Status:** Reference example reproduced independently.

The original chi-square calculation was tested against the paper's reference example.

| Quantity | Validated result |
|---|---:|
| Chi-square statistic | Approximately 2.60227 |
| Degrees of freedom | 4 |
| p-value | Approximately 0.62642 |

The expected regional counts, observed regional counts, test statistic, degrees of freedom, and p-value matched the independent calculation for this example.

Relevant validation scripts include `test_chisquare_reference_example.py` and `test_original_chisquare.py`.

This result validates the tested example and calculation path. It does not establish correctness for every possible input, all missing-data cases, or every statistical result reported in the paper.

## 6. Result-file analysis integration

The reproduction-side analysis workflow consists of:

- `result_file_adapter.py` — discovers supported filename conventions and extracts model names.
- `analysis_runner.py` — validates JSONL records before calling the original analysis functions.
- `test_result_file_adapter.py` — tests filename discovery and model-name extraction.
- `test_analysis_runner.py` — tests record validation and synthetic integration with the original analysis functions.

The integration tests use synthetic records. They demonstrate that the tested data path executes successfully, not that real model outputs have been reproduced.

Filename compatibility is not sufficient evidence that two result files represent the same experiment. Schema, evaluation category, and provenance must be verified before interpreting results.

## 7. Test status

**Latest reported result: 24 tests passed in 10.21 seconds.**

The test suite covers selected dataset-generation checks, metadata handling, filename conventions, statistical reference calculations, input validation, and synthetic analysis integration.

Passing tests support the specific assertions they exercise. They do not independently validate every claim made by the paper or guarantee the correctness of untested cases.

## 8. Reproducibility limitations

- No original model-level result files were found in the audited reference repository.
- The paper's complete model evaluations have not been independently rerun.
- The paper's reported model rankings, accuracy figures, and regional-bias findings have therefore not been independently reproduced by this project.
- No paid model API calls have been made.
- The original reference repository is intended to remain unchanged; corrections and adapters are maintained separately.

A complete model-level reproduction would require suitable existing result data or an explicitly documented execution strategy that satisfies the project's zero-cost constraint. Any changes to models, prompts, sampling procedures, run counts, or evaluation methods would need to be recorded as deviations.

## 9. Repository integrity

The audited reference checkout is at commit `bbde381`.

The latest reported Git status showed only generated `__pycache__` directories as untracked entries. After removing those directories, a blank `git status --short` output would confirm that the reference checkout has no reported working-tree changes.

## 10. Conclusion

The project has validated selected components of the INDICA dataset and analysis pipeline, identified two implementation-level issues, and established tests for a reproduction-side integration path.

The strongest supported conclusion is that **selected data-generation and statistical-analysis components have been checked against source behavior and reference examples**. The project should be presented as a code audit and partial reproduction, not as a completed reproduction of the paper's model-level findings.