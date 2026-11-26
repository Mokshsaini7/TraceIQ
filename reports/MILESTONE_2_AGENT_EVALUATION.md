# Milestone 2 Agent Evaluation Report

## Evaluation set

- Historical Milestone 1 seeded defects: **10** (Mozilla, Apache, Eclipse)
- Additional format fixtures: **8** (Python, Java, JavaScript, .NET, Go, Ruby, PHP, JSON)
- Expected labels are manually reviewed benchmark annotations; original seed data does not provide a complete standardized gold-label set.

## Triage Agent — historical seed accuracy

| Metric | Correct | Total | Accuracy |
|---|---:|---:|---:|
| Severity | 10 | 10 | 100.0% |
| Priority | 10 | 10 | 100.0% |
| Component | 10 | 10 | 100.0% |

## Log Analysis Agent — historical seed accuracy

| Metric | Correct | Total | Accuracy |
|---|---:|---:|---:|
| Exception Type | 10 | 10 | 100.0% |
| Failure Point | 10 | 10 | 100.0% |
| Code Path | 10 | 10 | 100.0% |

## Log Analysis Agent — synthetic format fixtures

| Metric | Correct | Total | Accuracy |
|---|---:|---:|---:|
| Exception Type | 8 | 8 | 100.0% |
| Failure Point | 8 | 8 | 100.0% |
| Code Path | 8 | 8 | 100.0% |
| Detected format | 8 | 8 | 100.0% |

## Input-shape resilience

- PASS — description only triage
- PASS — missing logs graceful
- PASS — logs without description graceful
- PASS — messy unstructured logs graceful

## Incorrect predictions and failure analysis

No mismatches were observed in this run.

## Improvements applied

- Added Mozilla/Gecko native C++ stack frame parsing (`module!symbol [file.cpp:line]`).
- Added Mozilla `function() at file.cpp:line` and assertion-location handling.
- Added extraction of `NS_ERROR_*` diagnostic identifiers and `AssertionFailure` messages.
- Corrected Java traces where the exception and first frame share one line so the leading frame is retained as the failure point.
- Preserved conservative behavior when no stack frame or structured exception evidence exists.

## Interpretation and limitations

- Historical seed set contains only 10 curated examples and is not statistically representative.
- Severity and priority labels are manual benchmark annotations because the source files do not provide a normalized ground-truth label for every issue.
- Confidence scores are evidence-coverage heuristics, not calibrated probabilities.
- Re-run after any parser/rule change with `python backend/scripts/run_agent_benchmark.py` from the project root.
