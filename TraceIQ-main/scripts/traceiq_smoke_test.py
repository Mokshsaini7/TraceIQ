"""Read-only TraceIQ smoke test using only Python's standard library.

Run: py scripts/traceiq_smoke_test.py
Override endpoints with TRACEIQ_BACKEND_URL / TRACEIQ_FRONTEND_URL.
"""
from __future__ import annotations
import json
import os
import sys
import urllib.error
import urllib.request

BACKEND = os.getenv("TRACEIQ_BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
FRONTEND = os.getenv("TRACEIQ_FRONTEND_URL", "http://127.0.0.1:5173").rstrip("/")
checks: list[tuple[str, str, str]] = []


def get(url: str, timeout: int = 8):
    req = urllib.request.Request(url, headers={"User-Agent": "TraceIQ-Smoke-Test/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read()
        content_type = response.headers.get("Content-Type", "")
        data = None
        if "json" in content_type:
            data = json.loads(body.decode("utf-8"))
        return response.status, data, body


def check(name: str, url: str, json_expected: bool = False):
    try:
        status, data, body = get(url)
        if status < 200 or status >= 300:
            checks.append(("FAIL", name, f"HTTP {status}"))
        elif json_expected and not isinstance(data, (dict, list)):
            checks.append(("FAIL", name, "Expected a JSON response"))
        else:
            checks.append(("PASS", name, f"HTTP {status}"))
        return data
    except urllib.error.HTTPError as exc:
        checks.append(("FAIL", name, f"HTTP {exc.code}"))
    except Exception as exc:
        checks.append(("FAIL", name, str(exc)[:180]))
    return None


print("TraceIQ read-only smoke test")
print("=" * 58)
check("Frontend responds", FRONTEND)
check("Backend root responds", BACKEND + "/")
health = check("Health endpoint responds", BACKEND + "/api/v1/health", True)
check("OpenAPI schema responds", BACKEND + "/openapi.json", True)
check("Submissions API responds", BACKEND + "/api/v1/submissions?page=1&page_size=1", True)
check("Knowledge base stats respond", BACKEND + "/api/v1/knowledge-base/stats", True)
check("Architecture endpoint responds", BACKEND + "/api/v1/system/architecture", True)

if isinstance(health, dict):
    db = health.get("database", {})
    emb = health.get("embeddings", {})
    if db.get("status") == "healthy":
        checks.append(("PASS", "Database health", f"Using {db.get('dialect', 'unknown')}"))
    else:
        checks.append(("WARN", "Database health", str(db.get("error") or db.get("status"))))
    if emb.get("status") == "healthy":
        checks.append(("PASS", "Embedding model", f"{emb.get('model_name')} is active"))
    else:
        checks.append(("WARN", "Embedding model", f"{emb.get('mode', emb.get('status'))}; hybrid search may use BM25 only"))
    if health.get("status") == "healthy":
        checks.append(("PASS", "Overall backend health", "healthy"))
    else:
        checks.append(("WARN", "Overall backend health", "degraded; inspect dependency details above"))

print("\nResults")
print("-" * 58)
for state, name, detail in checks:
    print(f"[{state}] {name}: {detail}")
passed = sum(x[0] == "PASS" for x in checks)
failed = sum(x[0] == "FAIL" for x in checks)
warned = sum(x[0] == "WARN" for x in checks)
print("-" * 58)
print(f"SUMMARY: {passed} PASS | {failed} FAIL | {warned} WARN")
if failed:
    print("RESULT: CHECK FAILED — fix the failed endpoints before testing diagnosis.")
    sys.exit(1)
if warned:
    print("RESULT: API IS REACHABLE, BUT SOME DEPENDENCIES ARE DEGRADED.")
else:
    print("RESULT: BASIC SERVICES LOOK HEALTHY. Run a real submission test next.")
