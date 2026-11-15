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
