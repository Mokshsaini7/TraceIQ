#!/usr/bin/env python3
"""Reproducible Milestone 2 benchmark for the seeded M1 defects and format fixtures."""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
from bugdiag.agents.triage_agent import TriageAgent
from bugdiag.agents.log_analysis_agent import LogAnalysisAgent


def load_historical():
    rows = []
    for path in sorted((ROOT / "datasets/raw").glob("*")):
        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix.lower() == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as handle:
                data = list(csv.DictReader(handle))
        else:
            continue
        for row in data:
            issue = row.get("bug_id") or row.get("issue_key") or row.get("id")
            if not issue:
                continue
            rows.append((issue, row))
    return rows


def accuracy(items):
    return round(sum(bool(x) for x in items) / len(items), 4) if items else 0.0


def evaluate():
    gold = json.loads((ROOT / "datasets/benchmarks/milestone2_gold_labels.json").read_text())
    triage_agent, log_agent = TriageAgent(), LogAnalysisAgent()
    triage_checks = {"severity": [], "priority": [], "component": []}
    log_checks = {"exception_type": [], "failure_point": [], "code_path": []}
    errors = []
    historical_rows = load_historical()
    for issue, row in historical_rows:
        expected = gold["historical"][issue]
        title = row.get("summary", "")
        description = row.get("description", "")
        stack = row.get("stack_trace") or row.get("environment_log") or ""
        logs = row.get("comments") or row.get("comment_log") or ""
        language = row.get("language")
        triage = triage_agent.analyze(title=title, description=description, stack_trace=stack,
                                     error_logs=logs, language_hint=language)
        log = log_agent.analyze(stack_trace=stack, error_logs=logs)
        checks = {
            "severity": triage.severity == expected["severity"],
            "priority": triage.priority == expected["priority"],
            "component": triage.affected_component == expected["component"],
            "exception_type": log.exception_type == expected["exception_type"],
            "failure_point": bool(log.failure_point and log.failure_point.file == expected["failure_file"]
                                   and log.failure_point.line == expected["failure_line"]),
            "code_path": [f.file for f in log.code_path] == expected["code_path"],
        }
        for name in triage_checks:
            triage_checks[name].append(checks[name])
        for name in log_checks:
            log_checks[name].append(checks[name])
        if not all(checks.values()):
            errors.append({"id": issue, "source": "historical", "failed_checks": [k for k,v in checks.items() if not v],
                           "predicted": {"severity": triage.severity, "priority": triage.priority,
                             "component": triage.affected_component, "exception_type": log.exception_type,
                             "failure_point": log.failure_point.model_dump() if log.failure_point else None,
                             "code_path": [f.file for f in log.code_path]}, "expected": expected})

    synthetic_checks = {"exception_type": [], "failure_point": [], "code_path": []}
    synthetic_format_checks = []
    for case in gold["synthetic_log_cases"]:
        result = log_agent.analyze(case.get("stack_trace"), case.get("error_logs"))
        checks = {
            "exception_type": result.exception_type == case["exception_type"],
            "failure_point": ((result.failure_point.file if result.failure_point else None) == case["failure_file"]
                              and (result.failure_point.line if result.failure_point else None) == case["failure_line"]),
            "code_path": [f.file for f in result.code_path] == case["code_path"],
        }
        for name in synthetic_checks:
            synthetic_checks[name].append(checks[name])
        synthetic_format_checks.append(result.detected_format == case["format"])
        if not all(checks.values()) or result.detected_format != case["format"]:
            errors.append({"id": case["id"], "source": "synthetic", "failed_checks": [k for k,v in checks.items() if not v] +
                           ([] if result.detected_format == case["format"] else ["detected_format"]),
                           "predicted": {"format": result.detected_format, "exception_type": result.exception_type,
                             "failure_point": result.failure_point.model_dump() if result.failure_point else None,
                             "code_path": [f.file for f in result.code_path]}, "expected": case})

    # Evidence-shape smoke checks: missing logs, log-only, description-only and messy mixed input.
    shape_results = {}
    description_only = triage_agent.analyze("Description-only defect", "A user cannot save a profile after editing a valid display name.")
    shape_results["description_only_triage"] = description_only.severity in {"critical", "high", "medium", "low"}
    no_evidence = log_agent.analyze(None, None)
    shape_results["missing_logs_graceful"] = no_evidence.confidence_score == 0 and no_evidence.failure_point is None
    log_only = log_agent.analyze(None, "2026-11-25 ERROR ValueError: invalid state at /srv/app.py:25")
    shape_results["logs_without_description_graceful"] = log_only is not None
    messy = log_agent.analyze(None, "[WARN] retrying... ???\n2026-11-25T10:00:00Z ERROR java.lang.IllegalStateException: closed\n at com.acme.Worker.run(Worker.java:88) trailing garbage")
    shape_results["messy_unstructured_logs_graceful"] = messy is not None and 0 <= messy.confidence_score <= 1

    report = {
        "benchmark_version": gold["benchmark_version"],
        "dataset": {"historical_seed_records": len(historical_rows),
                    "synthetic_format_cases": len(gold["synthetic_log_cases"]),
                    "source_files": ["mozilla_defects_sample.json", "apache_defects_sample.csv", "eclipse_defects_sample.json"]},
        "triage_historical_accuracy": {k: {"correct": sum(v), "total": len(v), "accuracy": accuracy(v)} for k,v in triage_checks.items()},
        "log_historical_accuracy": {k: {"correct": sum(v), "total": len(v), "accuracy": accuracy(v)} for k,v in log_checks.items()},
        "log_synthetic_accuracy": {k: {"correct": sum(v), "total": len(v), "accuracy": accuracy(v)} for k,v in synthetic_checks.items()},
        "synthetic_detected_format_accuracy": {"correct": sum(synthetic_format_checks), "total": len(synthetic_format_checks), "accuracy": accuracy(synthetic_format_checks)},
        "input_shape_smoke_checks": shape_results,
        "incorrect_predictions": errors,
        "failure_analysis": dict(Counter(check for err in errors for check in err["failed_checks"])),
        "limitations": ["Historical seed set contains only 10 curated examples and is not statistically representative.",
                        "Severity and priority labels are manual benchmark annotations because the source files do not provide a normalized ground-truth label for every issue.",
                        "Confidence scores are evidence-coverage heuristics, not calibrated probabilities."],
    }
    (ROOT / "reports/milestone2_agent_benchmark.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Milestone 2 Agent Evaluation Report", "", "## Evaluation set", "",
             f"- Historical Milestone 1 seeded defects: **{len(historical_rows)}** (Mozilla, Apache, Eclipse)",
             f"- Additional format fixtures: **{len(gold['synthetic_log_cases'])}** (Python, Java, JavaScript, .NET, Go, Ruby, PHP, JSON)",
             "- Expected labels are manually reviewed benchmark annotations; original seed data does not provide a complete standardized gold-label set.", "",
             "## Triage Agent — historical seed accuracy", "", "| Metric | Correct | Total | Accuracy |", "|---|---:|---:|---:|"]
    for k,v in report["triage_historical_accuracy"].items(): lines.append(f"| {k.replace('_',' ').title()} | {v['correct']} | {v['total']} | {v['accuracy']:.1%} |")
    lines += ["", "## Log Analysis Agent — historical seed accuracy", "", "| Metric | Correct | Total | Accuracy |", "|---|---:|---:|---:|"]
    for k,v in report["log_historical_accuracy"].items(): lines.append(f"| {k.replace('_',' ').title()} | {v['correct']} | {v['total']} | {v['accuracy']:.1%} |")
    lines += ["", "## Log Analysis Agent — synthetic format fixtures", "", "| Metric | Correct | Total | Accuracy |", "|---|---:|---:|---:|"]
    for k,v in report["log_synthetic_accuracy"].items(): lines.append(f"| {k.replace('_',' ').title()} | {v['correct']} | {v['total']} | {v['accuracy']:.1%} |")
    v=report["synthetic_detected_format_accuracy"]; lines.append(f"| Detected format | {v['correct']} | {v['total']} | {v['accuracy']:.1%} |")
    lines += ["", "## Input-shape resilience", ""]
    for k,v in shape_results.items(): lines.append(f"- {'PASS' if v else 'FAIL'} — {k.replace('_',' ')}")
    lines += ["", "## Incorrect predictions and failure analysis", ""]
    if not errors: lines.append("No mismatches were observed in this run.")
    for err in errors:
        lines.append(f"- **{err['id']}** ({err['source']}): {', '.join(err['failed_checks'])}")
    if report["failure_analysis"]:
        lines += ["", "Mismatch counts by field:"]
        for k,v in report["failure_analysis"].items(): lines.append(f"- {k}: {v}")
    lines += ["", "## Improvements applied", "",
              "- Added Mozilla/Gecko native C++ stack frame parsing (`module!symbol [file.cpp:line]`).",
              "- Added Mozilla `function() at file.cpp:line` and assertion-location handling.",
              "- Added extraction of `NS_ERROR_*` diagnostic identifiers and `AssertionFailure` messages.",
              "- Corrected Java traces where the exception and first frame share one line so the leading frame is retained as the failure point.",
              "- Preserved conservative behavior when no stack frame or structured exception evidence exists.", "",
              "## Interpretation and limitations", "",
              *[f"- {item}" for item in report["limitations"]],
              "- Re-run after any parser/rule change with `python backend/scripts/run_agent_benchmark.py` from the project root.", ""]
    (ROOT / "reports/MILESTONE_2_AGENT_EVALUATION.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"triage": report["triage_historical_accuracy"], "log_historical": report["log_historical_accuracy"],
                      "log_synthetic": report["log_synthetic_accuracy"], "format": report["synthetic_detected_format_accuracy"],
                      "input_shapes": shape_results, "mismatches": len(errors), "failure_analysis": report["failure_analysis"]}, indent=2))
    return 1 if any(not v for v in shape_results.values()) else 0

if __name__ == "__main__":
    raise SystemExit(evaluate())
