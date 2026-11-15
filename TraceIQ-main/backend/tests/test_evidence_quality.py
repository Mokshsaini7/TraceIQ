from bugdiag.agents.log_analysis_agent import LogAnalysisAgent
from bugdiag.agents.triage_agent import TriageAgent
from bugdiag.agents.root_cause_agent import RootCauseAgent
from bugdiag.agents.remediation_agent import RemediationAgent
from bugdiag.schemas.agent import TriageResult, LogAnalysisResult

def test_exception_without_frames_is_not_reported_as_stack_trace():
    result = LogAnalysisAgent().analyze("ValueError: bad input", None)
    assert result.exception_type == "ValueError"
    assert result.has_stack_trace is False
    assert result.stack_frames == []

def test_root_cause_does_not_call_weak_historical_match_strong():
    triage = TriageResult(category="Network", severity="medium", priority="p2",
        programming_language="Python", completeness_score=0.5)
    logs = LogAnalysisResult(has_stack_trace=False, exception_type="TimeoutError",
        error_message="request timed out", stack_frames=[], suspect_files=[], technical_evidence=[])
    result = RootCauseAgent().analyze("API timeout", "The request timed out while calling service", triage, logs, [
        {"defect_id":"d1", "source_repo":"Example", "original_issue_id":"EX-1",
         "title":"Similar timeout", "similarity_score":0.202}
    ])
    assert result.confidence <= 0.6
    assert any("none met the threshold" in item for item in result.supporting_evidence)
    assert not any("Strong historical" in item for item in result.supporting_evidence)

def test_triage_completeness_is_fraction_between_zero_and_one():
    result = TriageAgent().analyze("Short bug", "Short description")
    assert 0.0 <= result.completeness_score <= 1.0

def test_remediation_does_not_claim_dataset_note_is_verified_patch():
    triage = TriageResult(category="Network", severity="medium", priority="p2",
        programming_language="Python", completeness_score=0.5)
    logs = LogAnalysisResult(has_stack_trace=False, exception_type=None, error_message=None,
        stack_frames=[], suspect_files=[], technical_evidence=[])
    from bugdiag.schemas.agent import RootCauseResult
    root = RootCauseResult(identified_root_cause="Unknown", explanation="Need more evidence",
        confidence=0.2, supporting_evidence=[], historical_matches=[])
    result = RemediationAgent().analyze(triage, logs, root, [{
        "defect_id":"d1", "source_repo":"Example", "original_issue_id":"EX-1",
        "title":"Old issue", "similarity_score":0.4, "resolution":"Changed connection retry policy."
    }])
    assert result.verified_fixes == []
    assert result.suggested_fixes[0].is_verified_from_history is False
    assert "not independently checked" in result.suggested_fixes[0].description
    assert result.suggested_fixes[-1].diff_snippet is None
