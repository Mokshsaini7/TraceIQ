"""Milestone 2.1 triage tests: synthetic scenarios and bundled historical defects."""
import csv
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from bugdiag.agents.triage_agent import TriageAgent
from bugdiag.schemas.agent import TriageResult

agent = TriageAgent()

@pytest.mark.parametrize("case,expected_severity,expected_priority,component", [
    (dict(title="Production service outage", description="Production API gateway is unavailable for all users after deployment; entire service is down.", stack_trace="RuntimeError: service unavailable", reproduction_steps="Deploy build then call /health"), "critical", "p1", "API Gateway"),
    (dict(title="Authentication login broken", description="Users cannot log in because authentication requests fail for every account on the login workflow.", stack_trace="AuthController.java:91 NullPointerException", language_hint="Java"), "high", "p2", "AuthController"),
    (dict(title="API returns wrong response", description="A single API endpoint returns an incorrect response for a subset of valid requests; workaround is available.", stack_trace="ResponseMapper.py:30 ValueError", language_hint="Python"), "medium", "p3", "ResponseMapper"),
    (dict(title="Button alignment issue", description="The submit button is slightly misaligned on the settings page. This is a cosmetic UI alignment issue only."), "low", "p4", "Unknown"),
    (dict(title="Database connection failure", description="Database connection pool cannot establish a connection for this service; requests fail intermittently.", stack_trace="DatabaseConnection.py:88 ConnectionError", language_hint="Python"), "medium", "p3", "DatabaseConnection"),
    (dict(title="OutOfMemoryError in worker", description="A background worker exits with OutOfMemoryError while processing one large batch; other services remain available.", stack_trace="Worker.java:72 java.lang.OutOfMemoryError: Java heap space", language_hint="Java"), "high", "p2", "Worker"),
    (dict(title="NullPointerException in profile", description="The profile settings request throws NullPointerException when a user has no optional preferences.", stack_trace="UserProfileService.java:42 NullPointerException", language_hint="Java"), "medium", "p3", "UserProfileService"),
    (dict(title="Network timeout", description="A downstream request intermittently times out after 30 seconds. Retry succeeds and the rest of the application remains available.", stack_trace="Gateway.py:22 TimeoutError", language_hint="Python"), "medium", "p3", "Gateway"),
    (dict(title="SQL injection vulnerability", description="An exploitable SQL injection vulnerability allows remote attackers to read user records without authorization.", stack_trace="UserRepository.java:55 SQL query", language_hint="Java"), "critical", "p1", "UserRepository"),
    (dict(title="Deadlock in order worker", description="Two worker threads deadlock while updating the same order. The affected job queue stops processing.", stack_trace="OrderWorker.java:110 deadlock detected", language_hint="Java"), "high", "p2", "OrderWorker"),
    (dict(title="Incomplete bug report", description="The application sometimes fails. No further details are available."), "medium", "p3", "Unknown"),
    (dict(title="Ambiguous issue", description="Something is wrong with the application but the reporter cannot reproduce it."), "medium", "p3", "Unknown"),
    (dict(title="User says low but production is down", description="Production outage: all users cannot access the service. This is a release blocker.", user_severity="low", user_priority="p4"), "critical", "p1", "Unknown"),
    (dict(title="Unidentified exception", description="An unexpected error occurs in one form, but no module, endpoint, stack trace, or source file is supplied."), "medium", "p3", "Unknown"),
])
def test_synthetic_triage_scenarios(case, expected_severity, expected_priority, component):
    result = agent.analyze(**case)
    assert result.severity == expected_severity
    assert result.priority == expected_priority
    assert result.affected_component == component
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.reasoning.severity_reason
    assert result.reasoning.priority_reason
    assert result.reasoning.component_reason
    assert isinstance(result.reasoning.evidence, list)
    assert TriageResult.model_validate(result.model_dump())

def test_user_labels_are_not_blindly_trusted():
    result = agent.analyze(
        title="Small UI alignment defect",
        description="The settings page heading is slightly misaligned. Cosmetic only.",
        user_severity="critical", user_priority="p1",
    )
    assert (result.severity, result.priority) == ("low", "p4")

def test_component_unknown_without_evidence():
    result = agent.analyze(title="Bug report", description="An issue occurs but no technical details are known.")
    assert result.affected_component == "Unknown"
    assert any("component" in item.lower() for item in result.missing_information)

def test_confidence_is_bounded_and_evidence_sensitive():
    sparse = agent.analyze(title="Bug", description="It fails.")
    rich = agent.analyze(
        title="API request fails", description="The API request fails when a valid user submits a profile update.",
        stack_trace="ProfileService.py:31 ValueError", reproduction_steps="1. Login 2. Update profile",
        language_hint="Python"
    )
    assert 0 <= sparse.confidence_score <= 1
    assert rich.confidence_score > sparse.confidence_score

def test_schema_rejects_invalid_severity_and_confidence():
    result = agent.analyze(title="Bug report", description="A short report of a functional issue.")
    payload = result.model_dump()
    payload["severity"] = "urgent"
    with pytest.raises(ValidationError):
        TriageResult.model_validate(payload)
    payload = result.model_dump()
    payload["confidence_score"] = 1.5
    with pytest.raises(ValidationError):
        TriageResult.model_validate(payload)

def test_historical_mozilla_defects_smoke():
    rows = json.loads(Path("../datasets/raw/mozilla_defects_sample.json").read_text(encoding="utf-8"))
    assert rows
    for row in rows:
        result = agent.analyze(
            title=row.get("summary", ""), description=row.get("description", ""),
            stack_trace=row.get("stack_trace", ""), error_logs=row.get("comments", ""),
            language_hint=row.get("language")
        )
        assert result.severity in {"critical", "high", "medium", "low"}
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.affected_component != "Unknown"

def test_historical_eclipse_defects_smoke():
    rows = json.loads(Path("../datasets/raw/eclipse_defects_sample.json").read_text(encoding="utf-8"))
    assert rows
    for row in rows:
        result = agent.analyze(
            title=row.get("summary", ""), description=row.get("description", ""),
            stack_trace=row.get("stack_trace", ""), error_logs=row.get("comments", ""),
            language_hint=row.get("language")
        )
        assert result.severity in {"critical", "high", "medium", "low"}
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.affected_component != "Unknown"

def test_historical_apache_defects_smoke():
    with Path("../datasets/raw/apache_defects_sample.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    for row in rows:
        result = agent.analyze(
            title=row.get("summary", ""), description=row.get("description", ""),
            stack_trace=row.get("environment_log", ""), error_logs=row.get("comment_log", ""),
            language_hint=row.get("language")
        )
        assert result.severity in {"critical", "high", "medium", "low"}
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.affected_component != "Unknown"


@pytest.mark.parametrize("description,expected_priority", [
    ("A medium impact defect is confirmed, but this is an active production incident requiring immediate response.", "p1"),
    ("A limited functional issue has no workaround and blocks a major workflow for the release today.", "p1"),
    ("A normal API defect affects a subset of requests and has a safe workaround.", "p3"),
    ("A cosmetic alignment issue can be fixed in a later release.", "p4"),
])
def test_priority_uses_urgency_and_impact(description, expected_priority):
    result = agent.analyze(title="Priority assessment", description=description)
    assert result.priority == expected_priority
    assert result.reasoning.priority_reason


def test_priority_and_severity_are_independent_of_reporter_suggestions():
    result = agent.analyze(
        title="Production login outage",
        description="Production login is unavailable for all users and is an active customer-facing incident.",
        user_severity="low", user_priority="p4",
    )
    assert result.severity == "critical"
    assert result.priority == "p1"
