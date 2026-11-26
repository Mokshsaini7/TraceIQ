"""Milestone 2 regression/evaluation tests for historical and newly submitted bug shapes."""
import json
import runpy
from pathlib import Path

from bugdiag.agents.log_analysis_agent import LogAnalysisAgent
from bugdiag.agents.triage_agent import TriageAgent

ROOT = Path(__file__).resolve().parents[2]


def test_mozilla_gecko_native_and_assertion_frames():
    trace = """Assertion failure: expected != nullptr, at js/src/jit/WarpBuilder.cpp:1423
#01: js::jit::WarpBuilder::buildGetProperty(js::jit::BytecodeLocation) [js/src/jit/WarpBuilder.cpp:1425]
#02: js::jit::WarpBuilder::build() [js/src/jit/WarpBuilder.cpp:890]
#03: js::jit::CompileBackEnd(js::jit::MIRGenerator*) [js/src/jit/Ion.cpp:1740]"""
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.detected_format == "mozilla_cpp"
    assert result.exception_type == "AssertionFailure"
    assert result.failure_point.file == "js/src/jit/WarpBuilder.cpp"
    assert result.failure_point.line == 1423
    assert [frame.line for frame in result.code_path] == [1423, 1425, 890, 1740]


def test_one_line_jvm_export_preserves_frame_order():
    trace = ("java.lang.OutOfMemoryError: Java heap space "
             "at org.apache.spark.memory.TaskMemoryManager.allocatePage(TaskMemoryManager.java:310) "
             "at org.apache.spark.util.collection.unsafe.sort.UnsafeExternalSorter.grow(UnsafeExternalSorter.java:234) "
             "at org.apache.spark.sql.execution.joins.SortMergeJoinExec.doExecute(SortMergeJoinExec.scala:189)")
    result = LogAnalysisAgent().analyze(trace, None)
    assert [f.file for f in result.code_path] == ["TaskMemoryManager.java", "UnsafeExternalSorter.java", "SortMergeJoinExec.scala"]
    assert result.failure_point.file == "TaskMemoryManager.java"
    assert result.failure_point.line == 310


def test_description_only_and_logs_only_submission_shapes():
    triage = TriageAgent().analyze("Profile save defect", "A user cannot save a profile after editing a valid display name.")
    assert triage.severity in {"critical", "high", "medium", "low"}
    empty = LogAnalysisAgent().analyze(None, None)
    assert empty.failure_point is None and empty.confidence_score == 0
    logs_only = LogAnalysisAgent().analyze(None, "ERROR ValueError: invalid state")
    assert logs_only.exception_type == "ValueError"


def test_milestone2_seeded_and_synthetic_benchmark_has_no_regressions():
    namespace = runpy.run_path(str(ROOT / "backend/scripts/run_agent_benchmark.py"))
    assert namespace["evaluate"]() == 0
    report = json.loads((ROOT / "reports/milestone2_agent_benchmark.json").read_text())
    assert report["dataset"]["historical_seed_records"] == 10
    assert report["dataset"]["synthetic_format_cases"] == 8
    for metric in report["triage_historical_accuracy"].values():
        assert metric["accuracy"] == 1.0
    for metric in report["log_historical_accuracy"].values():
        assert metric["accuracy"] == 1.0
    for metric in report["log_synthetic_accuracy"].values():
        assert metric["accuracy"] == 1.0
    assert report["synthetic_detected_format_accuracy"]["accuracy"] == 1.0
    assert all(report["input_shape_smoke_checks"].values())
    assert report["incorrect_predictions"] == []
