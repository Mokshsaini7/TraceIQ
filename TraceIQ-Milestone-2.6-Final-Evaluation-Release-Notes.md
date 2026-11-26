# TraceIQ Milestone 2.6 — Final Milestone 2 Evaluation & Release Notes

## Scope delivered

This release completes the four connected Milestone 2 capabilities in the existing TraceIQ application:

1. **First-level Bug Triage Agent** — severity (`critical`, `high`, `medium`, `low`), independent priority (`p1`–`p4`), component identification, evidence-based confidence, and concise reasoning.
2. **Stack Trace & Log Analysis Agent** — exception/error extraction, message extraction, file/class/method/line failure point, ordered code path, format detection, and bounded confidence.
3. **Automatic intake orchestration** — new submissions invoke both agents; results and per-agent status are persisted in a versioned combined context for downstream diagnosis/Milestone 3 agents. Missing evidence and isolated agent failures are represented explicitly.
4. **Evaluation and continuous improvement** — labelled historical and synthetic fixtures, field-level accuracy metrics, mismatch reporting, parser/rule improvements, and repeatable regression tests.

## Test set and results

- 10 historical seed defects: 4 Mozilla, 4 Apache, 2 Eclipse.
- 8 synthetic format fixtures: Python, Java, JavaScript, .NET, Go, Ruby, PHP, and JSON.
- Additional shape checks: description only, stack trace + description, logs without description, no logs, and messy/unstructured logs.

| Agent | Metric | Result |
|---|---|---:|
| Triage | Severity accuracy (historical) | 10/10 — 100% |
| Triage | Priority accuracy (historical) | 10/10 — 100% |
| Triage | Component accuracy (historical) | 10/10 — 100% |
| Log Analysis | Exception type (historical) | 10/10 — 100% |
| Log Analysis | Failure point (historical) | 10/10 — 100% |
| Log Analysis | Ordered code path (historical) | 10/10 — 100% |
| Log Analysis | Exception, failure point, code path, format (synthetic) | 8/8 each — 100% |

The exact run output is in `reports/milestone2_agent_benchmark.json`; methodology and error analysis are in `reports/MILESTONE_2_AGENT_EVALUATION.md`.

## Improvements made after the first benchmark pass

- Historical Mozilla frames initially were not recognized. Added Gecko native `module!symbol [source.cpp:line]` and `function() at file.cpp:line` parsing.
- Assertion failures initially missed the assertion source location. Added explicit assertion-location extraction and `AssertionFailure` classification.
- Mozilla `NS_ERROR_*` identifiers were not extracted as error types. Added native error-token recognition.
- One-line Jira/JVM logs initially reordered frames or lost Scala frames. Added an ordered inline JVM scan supporting `.java`, `.kt`, and `.scala`.
- Severity/priority expected labels were reviewed against stated scope and urgency; the redirect/CORS issue was labelled medium/normal because the supplied record did not establish a broad outage or security exploit.

The final regression run has zero mismatches against the current manually annotated benchmark.

## Verification

- Backend test suite: **64 passed**.
- Python compilation: verified.
- Benchmark: **zero current mismatches** across the 10 historical and eight synthetic fixtures.
- Frontend production build: not verified in this environment because the npm package cache did not contain all locked dependencies (`npm ci --offline` failed with `ENOTCACHED`). Run `npm ci` and `npm run build` on a machine with registry access.

## Important limitations

- The historical corpus is only 10 curated records, not a statistically representative benchmark.
- The raw historical records do not contain normalized labels for every metric. Severity and priority expectations are documented manual annotations, not original upstream labels.
- The 100% result is benchmark agreement on this small fixture set, not a production accuracy guarantee. Expand the independently labelled dataset before making external performance claims.
- Confidence values are deterministic evidence-coverage scores, not calibrated probabilities.
- The application is not yet production-hardened for public multi-user deployment; follow the existing reliability/deployment documentation for authentication, authorization, background job durability, monitoring, and operational controls.

## Repeat the evaluation

From the project root:

```bash
python backend/scripts/run_agent_benchmark.py
cd backend && pytest -q
```
