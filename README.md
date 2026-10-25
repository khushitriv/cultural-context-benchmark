# Cultural-Context Evaluation and Benchmarking

This is a cultural context accuracy benchmark project which is built on insights from a Partial reproduction and audit of an existing research project and paper titled "*Common to **Whom**? Regional Cultural Common Sense and LLM Bias in India.*"

The link to the research paper is as follows: xxx

This project is divided into two parts:

First the research reproduction and audit of INDICA - a research pipeline for evaluating regional cultural common sense and LLM bias in India. This section is covered inside the "reference" and "reproduction" folders in the repository.

And secondly, An independent benchmark, which is under development, to investigate how accurately language models handle culturally specific questions about India and South Asia.

The project connects reproducibility-focused research with the development of an independent evaluation framework.

## Table of Contents

- [Motivation](#motivation)
- [Project Components](#project-components)
- [Research reproduction work](#1-indica-research-reproduction-and-code-audit)
- [Cultural-Context Accuracy Benchmark (CCAB)](#2-cultural-context-accuracy-benchmark-ccab)
- [Technology Stack](#technology-stack)
- [Reproducibility and Testing](#reproducibility-and-testing)
- [Current Status](#current-status)
- [Limitations](#limitations)
- [References](#references)

## Motivation

Cultural knowledge is not always uniform across regions.

A response that appears reasonable in one cultural context may be incomplete, inaccurate, or inappropriate in another. Evaluating language models on culturally grounded questions therefore requires attention to regional variation, question design, scoring methodology, and the limitations of evaluation datasets.

This project explores these challenges through two complementary activities: examining the implementation of existing research and developing an independent benchmark for cultural context accuracy.

## Project Components

### 1. Research Reproduction and Code Audit

This component examines the implementation of the published research pipeline.

The goal is to validate selected aspects of the released code and data against the paper, identify implementation inconsistencies, and test supporting analysis utilities.

### 2. Cultural-Context Accuracy Benchmark (CCAB)

CCAB is an independent research effort. It aims to evaluate language model responses to culturally specific questions related to India and South Asia.

The benchmark is being developed as a separate contribution with its own question design, evaluation methodology, and planned comparative analysis.

## 1. Reproduction and Audit

**Reference paper:** *Common to Whom? Regional Cultural Commonsense and LLM Bias in India*

- Paper: [arXiv:2601.15550](https://arxiv.org/abs/2601.15550)
- Original repository: [INDICA on GitHub](https://github.com/Sangmitra-06/INDICA)

### Scope of the audit

The Work focused on examining the dataset question generation pipeline result file integration and selected statistical calculations.

The audit included:

- Dataset validation: Checked dataset statistics and regional question–answer counts against the published paper.
- Question-generation analysis: Examined generated multiple-choice questions, completeness, option counts, and answer-sharing statistics.
- Implementation audit: Identified inconsistencies in dataset metadata handling and result-file discovery.
- Statistical verification: Independently checked selected chi-square calculations against a documented example.
- Testing and integration: Developed validation utilities, an analysis adapter, and synthetic integration tests to assess selected parts of the workflow.

### Findings

Two implementation inconsistencies were identified:

1. Dataset metadata mismatch: The question-generation implementation reads `question_category`, whereas the audited dataset uses `question_domain`. A separate reproduction-side utility was developed to address this mapping issue without modifying the original reference repository.
2. Result-file discovery mismatch: The result logger and the chi-square analysis script use different filename patterns, potentially preventing the analysis script from discovering the logger's standard output files.

These findings concern implementation and pipeline integration. They do not, by themselves, establish that the paper's reported conclusions are incorrect.

### Testing

The reproduction-side test suite reached 24 passing tests, covering validation utilities, metadata handling, analysis integration, and synthetic pipeline scenarios.

These tests support the correctness of the tested components. However, they do not constitute a full reproduction of the paper's model-level experiments.

### Scope and limitations

This work is a partial research reproduction and code audit, not a complete reproduction of all reported experimental results.

The original model-level evaluation was not independently rerun in full. Consequently, the paper's reported model-performance findings should be understood as published results rather than independently reproduced findings.

## 2. Cultural-Context Accuracy Benchmark (CCAB)

Status: In progress

CCAB is an independent benchmark being developed to investigate the cultural-context accuracy of language models on questions relating to India and South Asia.

Where the first component focuses on existing research implementation CCAB focuses on developing an independent evaluation framework.

### Research objectives

- Develop a structured collection of culturally specific questions.
- Explore evaluation of both multiple-choice and open-ended model responses.
- Establish reference answers and a human-reviewed scoring process.
- Compare model performance across questions and cultural categories.
- Analyze recurring errors and areas where model responses may lack cultural specificity.
- Use appropriate statistical methods to quantify performance differences and uncertainty.
- Prioritize reproducible experiments using freely accessible tools and models where feasible.

### Planned evaluation methodology

The benchmark is intended to support analysis at multiple levels:

- Overall performance: How accurately does each evaluated model answer the questions?
- Category-level performance: Does performance vary across cultural topics?
- Response-type comparison: Do results differ between multiple-choice and open-ended questions?
- Error analysis: What types of cultural misunderstandings or inaccuracies occur?
- Statistical uncertainty: How robust are observed differences between models?

These are development goals, not claims of completed experiments. Dataset size, evaluated models, scoring procedures, and statistical methods will be documented as the implementation progresses.

### Role of previous research reproduction

The partial reproduction and audit of the published paper works as a reference and provides practical experience in examining cultural-evaluation datasets, checking research implementations, and validating statistical workflows.

CCAB uses that experience as input to an independent benchmark-development effort. It is not a reproduction of it's dataset or a claim to authorship of the original paper.

## Technology Stack

The repository's research and validation work uses or is organized around:

- Python: data processing, validation, and analysis.
- pytest: automated testing.
- Statistical analysis: validation of selected statistical calculations and development of evaluation methods.
- LLM evaluation tooling: intended for the independent CCAB experiments as the evaluation pipeline develops.

The exact dependencies and environment setup should be maintained in the repository's dependency files as the implementation evolves.

## Reproducibility and Testing

Reproducibility is a central consideration across both components.

The INDICA audit includes automated tests and synthetic integration scenarios to verify selected pipeline behavior without requiring the original large-scale model evaluation.

To run the reproduction test suite from the repository root, use:

```bash
python -m pytest ./reproduction -v
```

The audited test suite completed with 24 passing tests in the recorded run. Results may vary if the environment or code changes.

For future CCAB experiments, the intended practice is to document the dataset version, model identifiers, prompts, scoring rules, random seeds where applicable, and evaluation settings so results can be interpreted and reproduced.

## Current Status

| Component | Status |
|---|---|
| Paper dataset and question-generation checks | Completed for the audited scope |
| Selected statistical calculations | Independently checked |
| Audit utilities and synthetic tests | Implemented; 24 tests passed |
| Full paper model-level reproduction | Not completed |
| CCAB research design and benchmark development | In progress |
| Large-scale CCAB model evaluation | Planned |
| CCAB comparative results and error analysis | Pending implementation and experiments |

## Limitations

- The audit covers selected implementation and statistical aspects, not every part of the paper's experimental workflow.
- Synthetic integration tests do not replace tests using the original model outputs.
- Identifying code inconsistencies does not automatically demonstrate that reported research findings are invalid.
- CCAB is under development; its final dataset, model coverage, scoring methodology, and findings have not yet been established.
- Cultural reference answers and human review require careful documentation of the validation process and its limitations.
- Free inference availability, computational resources, and model access may constrain the scale of future experiments.

## References

1. *Common to Whom? Regional Cultural Commonsense and LLM Bias in India.* [Read the paper](https://arxiv.org/abs/2601.15550).

2. Original implementation: [Sangmitra-06/INDICA](https://github.com/Sangmitra-06/INDICA).
