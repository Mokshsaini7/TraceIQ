"""Tests for scoring fix, CORS parsing, citation rule, dashboard stats and deletion."""

import pytest
from fastapi.testclient import TestClient
from bugdiag.main import app
from bugdiag.database.session import init_db
from bugdiag.core.config import Settings
from bugdiag.llm.enhancer import LLMEnhancer

@pytest.fixture(autouse=True)
def _db():
    init_db()

def test_cors_accepts_comma_separated():
    s = Settings(CORS_ORIGINS="http://a.com, http://b.com")
    assert s.CORS_ORIGINS == ["http://a.com", "http://b.com"]

def test_cors_accepts_json_list():
    assert Settings(CORS_ORIGINS='["http://a.com"]').CORS_ORIGINS == ["http://a.com"]

def test_citation_rule():
    allowed = {"MOZ-1", "ECL-2"}
    assert LLMEnhancer.validate_citations("Caused by X [MOZ-1].", allowed)
    assert not LLMEnhancer.validate_citations("No citations here.", allowed)
    assert not LLMEnhancer.validate_citations("Fake cite [FAKE-9].", allowed)

def test_unrelated_query_is_not_flagged_duplicate():
    with TestClient(app) as c:
        r = c.post("/api/v1/search/historical", json={"query": "zzqx unrelated gardening recipe", "method": "hybrid", "top_k": 3})
        assert r.status_code == 200
        items = r.json()["results"]
        assert all(i["similarity_score"] < 0.78 for i in items)

def test_dashboard_stats_and_delete():
    with TestClient(app) as c:
        r = c.post("/api/v1/submissions", json={"title": "Delete me please", "description": "Temporary submission for deletion test"})
        assert r.status_code == 201
        sid = r.json()["id"]
        stats = c.get("/api/v1/stats/dashboard").json()
        assert stats["total_submissions"] >= 1 and "knowledge_base" in stats
        assert c.delete(f"/api/v1/submissions/{sid}").status_code == 204
        assert c.get(f"/api/v1/submissions/{sid}").status_code == 404
        assert c.delete(f"/api/v1/submissions/{sid}").status_code == 404

def test_sort_by_whitelist():
    with TestClient(app) as c:
        assert c.get("/api/v1/submissions?sort_by=__class__").status_code == 200


def test_submission_automatically_runs_and_persists_both_intake_agents():
    cases = [
        {
            "title": "Python database timeout on checkout",
            "description": "Checkout requests fail when the database connection pool times out for active customers.",
            "stack_trace": "Traceback (most recent call last):\n  File \"app/checkout.py\", line 42, in submit\n    raise TimeoutError('database timeout')\nTimeoutError: database timeout",
            "error_logs": "ERROR checkout: database connection timeout",
            "programming_language": "Python",
        },
        {
            "title": "Missing diagnostic evidence report",
            "description": "The settings page occasionally fails to save a user's display preferences.",
        },
        {
            "title": "Java null pointer in profile service",
            "description": "Profile reads fail for users without optional profile metadata.",
            "stack_trace": "java.lang.NullPointerException: profile is null\n at com.example.ProfileService.load(ProfileService.java:87)",
            "error_logs": "ERROR ProfileService - profile is null",
            "programming_language": "Java",
        },
    ]
    with TestClient(app) as client:
        for case in cases:
            response = client.post("/api/v1/submissions", json=case)
            assert response.status_code == 201, response.text
            payload = response.json()
            context = payload["analysis_context"]
            assert context["schema_version"] == "1.0"
            assert context["triage_status"] == "completed"
            assert context["triage_output"]["severity"] in {"critical", "high", "medium", "low"}
            assert context["triage_output"]["priority"] in {"p1", "p2", "p3", "p4"}
            assert "triage" in context["combined_context"]
            assert "log_analysis" in context["combined_context"]
            sid = payload["id"]
            persisted = client.get(f"/api/v1/submissions/{sid}/context")
            assert persisted.status_code == 200
            assert persisted.json()["combined_context"]["submission_id"] == sid
            if not case.get("stack_trace") and not case.get("error_logs"):
                assert context["log_analysis_status"] == "incomplete"
                assert context["log_analysis_output"]["confidence_score"] == 0.0
            else:
                assert context["log_analysis_status"] == "completed"


def test_submission_context_survives_one_agent_failure(monkeypatch):
    from bugdiag.services import submission_service

    class BrokenTriage:
        def analyze(self, **kwargs):
            raise RuntimeError("triage test failure")

    monkeypatch.setattr(submission_service, "TriageAgent", BrokenTriage)
    with TestClient(app) as client:
        response = client.post("/api/v1/submissions", json={
            "title": "Agent failure should be isolated",
            "description": "The service returns an intermittent failure during profile retrieval.",
            "stack_trace": "ValueError: invalid profile id",
        })
        assert response.status_code == 201, response.text
        context = response.json()["analysis_context"]
        assert context["triage_status"] == "failed"
        assert context["log_analysis_status"] == "completed"
        assert context["orchestration_status"] == "partial"
        assert context["errors"]
