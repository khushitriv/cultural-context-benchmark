# Cultural-Context Evaluation and Benchmarking

How well do language models handle culturally specific knowledge about India? This repository combines two lines of work: **audits of existing research** on cultural evaluation of language models (the first case study is INDICA, a recent benchmark of regional cultural commonsense), and **CCAB**, a new benchmark of accuracy on Gujarati Hindu cultural practices.

## Project Highlights

- Audit: studied existing published work to understand the domain. In the first case study (INDICA), this project recomputes the headline dataset statistics from the released data, finds and documenteds two pipeline bugs, and builts a 24-test suite and adapter layer around the original code without modifying it.
- Audit: checked the chi-square bias test against an independent calculation on a worked example.
- CCAB: a multiple-choice benchmark with human-verified answers, distractors tagged by where each wrong practice comes from, and per-item statistics.
- CCAB: validated schema, spreadsheet-to-dataset importer, answer-leak checks, evaluation runner, and statistics module, all covered by unit tests.

## Table of Contents

- [Background: the first case study (INDICA)](#background-the-first-case-study-indica)
- [Part 1: Audits of existing research](#part-1-audits-of-existing-research)
- [Part 2: CCAB](#part-2-ccab)
- [How the two parts connect](#how-the-two-parts-connect)
- [Repository layout](#repository-layout)
- [Getting started](#getting-started)
- [Current Status](#current-status)
- [Scope notes](#scope-notes)
- [Limitations](#limitations)
- [References](#references)


## Background: the first case study (INDICA)

*Common to Whom? Regional Cultural Commonsense and LLM Bias in India* (Madhusudan et al., 2026; [arXiv:2601.15550](https://arxiv.org/abs/2601.15550)) collects answers to 515 everyday-life questions from five Indian regions (1,630 region-specific answers) and finds that only 39.4% of the questions where all five regions answered get the same answer everywhere. It evaluates eight models two ways: region-anchored short answers (RASA), where models reach 13.4% to 20.9% fully correct, and region-agnostic multiple choice (RA-MCQ), where models choose Central and North Indian practices more often than expected.

## Part 1: Audits of existing research

**Goal:** Part of building CCAB was learning the domain by examining published work on it. Each audit takes one paper's released code and data and checks whether they reproduce the paper's setup. The first case study is INDICA. I picked it as a concrete place to start, I don't claim it better than the alternatives, and further papers may be audited the same way: an unmodified `reference/` copy of the authors' code, with my own checks alongside it.

### Case study 1: INDICA

#### Approach: 

The scripts import the authors' code from `reference/` and call it directly, so every check exercises the real implementation. Fixes live in separate adapter code and the reference folder stays unchanged through the project.

#### What I checked:

| Check | Result |
|---|---|
| Questions in released dataset | 515, as in the paper |
| Region-specific answers | 1,630, as in the paper |
| Questions where all five regions agree | 52, as in the paper |
| Questions with a consensus answer: West / Central / North / South / East | 354 / 348 / 326 / 326 / 276, as in the paper |
| RA-MCQ items generated from the dataset | 79 (32 with all five regions, 47 partial) |
| Chi-square test | Original code matches an independent scipy calculation on a worked example (chi-square 2.60227, df 4, p 0.62642) |

#### Findings:

1. *Result files are not found by the chi-square script.* `ChiSquareTest.py` searches for `*_ADVERSARIAL_MCQ_results.jsonl`, while the logger and `RAMCQ_bias_detection.py` use `*_RA_MCQ_results.jsonl`. `result_file_adapter.py` finds both styles.
2. *Generated MCQs lose their category.* `RAMCQ_creation.py` reads `question_category`, but the dataset field is `question_domain`, so all 79 MCQs end up without a category and the per-domain breakdown collapses into one bucket. `ramcq_metadata_fix.py` restores the mapping without changing question content.

Both are implementation inconsistencies in the released repository; they do not change the paper's conclusions. Full details are in `reproduction/audit_findings.md`.

An open question for follow-up: The chi-square script pools every repeated run of every question into one test. Repeated answers to the same question are likely correlated, so resampling over questions would be a more conservative check.

#### Tests:

 `python -m pytest reproduction -v` runs 24 tests offline, with no API keys. They cover MCQ generation and metadata, fractional-credit bias scoring, invalid-response handling, the chi-square implementation, option shuffling, and result-file discovery and validation.

## Part 2: CCAB

**Research question:** INDICA shows that with no region given, models lean toward Central and North Indian practices. CCAB asks a finer-grained, checkable version: when asked about one community's practices, do models give the correct answer, and when they're wrong, what do they answer instead?

#### Benchmark design

- About 150 four-option multiple-choice questions on Gujarati Hindu traditions, after a 30 to 50 item pilot. Categories: weddings, festivals and rituals, food and fasting, terminology, social norms, and minimal pairs.
- Every correct answer is written and checked by someone who knows the tradition, and a second person answers a blind subset to measure agreement. Models never decide the answer key.
- Every wrong option is a real practice from elsewhere and is tagged by source: another region, another Gujarati community, a Western default, or other. Wrong picks therefore show which defaults a model falls back on.
- Minimal pairs test whether a model changes its answer when only the cultural cue changes.
- Items carry a `community` tag (`common`, or a specific community once at least 30 items can be verified).

#### Method:

1. Questions are written in a spreadsheet and converted to a validated dataset.
2. A checker flags malformed items, near-duplicates, and unbalanced answer positions.
3. Shortcut baselines (longest option, most hedging words, fixed position) must score near chance, otherwise the item wording leaks the answer.
4. Each question is asked under several shuffled option orders at low temperature through OpenRouter, with cached responses.
5. Results come with Wilson 95% confidence intervals per model, category, and community. Models are compared with paired tests (exact McNemar, paired bootstrap, Holm correction), and wrong answers are analysed by distractor source with item-level bootstrapping.

#### Built so far:

- Single-source item schema with validator and unit tests
- Spreadsheet importer that balances answer positions
- Shortcut-baseline checks
- Evaluation runner with option shuffling, answer parsing, caching, and offline mock models
- Statistics module and report generator

**Next:** pilot questions, second-verifier check, full question set, model runs, error analysis, datasheet and write-up.

## How the two parts connect

CCAB is independent of INDICA and shares none of its data or code. Working through INDICA showed me where there was room to go deeper: its limitations section leaves finer-grained analysis and areas like marriage for future work. The audit also shaped how I built CCAB, with a single schema definition, explicit run-file paths, and per-question statistics.

| | INDICA | CCAB |
|---|---|---|
| Granularity | 5 regions | One tradition, community tags |
| Answer format | Free text (RASA), options without a single right answer (RA-MCQ) | Multiple choice, one verified answer |
| Ground truth | 4 of 5 regional participants agree | Author-written, second-person verified |
| Scoring | LLM judge with partial credit | Exact match, no judge |

## Repository layout

    reference/INDICA/   authors' repository (CC BY 4.0), unmodified
    reproduction/       audit code, adapters, tests, audit_findings.md

    data/review/         where CCAB questions are written
    data/draft/         generated dataset
    schemas/            generated item schema
    src/                CCAB importer, validator, baselines, runner, statistics, report
    tests/              CCAB unit tests
    docs/               datasheet and protocol

## Getting started
    ```bash
    pip install -r requirements.txt

    # audit
    python -m pytest reproduction -v
    ```
    ```bash
    # CCAB
    # (under development)
    # The Cultural-Context Accuracy Benchmark (CCAB) is under active development. The current implementation includes a draft question dataset, dataset validation and auditing utilities, and a review-sheet workflow.

    # The dataset validation and review-sheet export workflows are still being refined. Automated testing, model evaluation, statistical analysis, and report generation remain in development.

    # Usage instructions will be added once the corresponding workflows are implemented and verified. 
    ```

Real models run through OpenRouter; set `OPENROUTER_API_KEY` in your environment and do not commit it.

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

## Scope notes

The audit covers the RA-MCQ half of INDICA using the released dataset and code, and cites the paper's model results as published. CCAB focuses on one tradition and measures recognition through multiple choice; practices vary between families, so each item records known variation.

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

BibTeX entries for all cited work are collected in [`references.bib`](references.bib).

`reference/` is the authors' work under CC BY 4.0 (see `reference/INDICA/LICENSE`). I am not affiliated with the authors. Everything else is mine.