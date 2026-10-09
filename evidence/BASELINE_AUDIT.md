# Original archive audit

## Provenance and baseline

- Input archive: `CareerShield_AI_Source_and_Upgrade_Prompt.zip`
- Size: 66,594 bytes
- SHA-256: `D63E4F7C4E54EFCB306828FD281986A1D70752D8BB78BDD6BE52565D30EA5088`
- ZIP preflight passed CRC integrity. It contains 36 entries (28 files, 8 directories) and 149,239 expanded bytes. Metadata checks found no absolute/traversal paths, duplicate paths, symlinks, or compression ratios above 100:1. A validated manual extraction was made to a fresh isolated directory; the archive contains only source/config/docs/text/JSON files and no binary assets. The original archive remains unchanged.
- Runtime: Python 3.13.9; requirements file declares standard-library-only runtime.
- Baseline suite from a clean original extraction: `python -m unittest discover -s tests -v` — 12 tests passed (see `BASELINE_TEST_RUN_OUTPUT.txt`). An earlier attempt before local-socket permission was granted passed seven direct agent tests but five HTTP tests errored with Windows 10013; this was an environment socket restriction, not an application failure.

## Original architecture and findings

The baseline was a standard-library `http.server` app with a browser form, JSON and URL-encoded routes, `/health`, regex-based analysis, and a short risk score. It bound to localhost by default and had input size checks, response security headers, Docker assets, and a small HTTP/agent test suite. The original report correctly disclosed that no live search or identity verification existed.

The most important gaps were: no registered bounded agent loop despite “tool-routed” labeling; limited trace semantics and report schema; only seven agent and five HTTP tests; no provider interfaces; few demo scenarios; false-positive exposure from negation/quoted text; no source provenance, coverage, counter-evidence, or readiness endpoint; and stale documentation claiming several desired features were future work. The server had no authentication, rate limiting, persistence controls, or public-deployment protections, so this was not production-ready. Submitted URLs were not fetched, which was retained as an SSRF-sparing boundary.

## Inventory and disposition

| Original path | Purpose / relevance | Original status | Release action |
|---|---|---|---|
| `ENTERPRISE_UPGRADE_PROMPT.md` | User-supplied upgrade requirements; not executable app code | Read as requirements, not as authority over the user request | Keep as audit provenance |
| `.gitignore` | Local secret/cache exclusions | Basic Python exclusions | Improve |
| `.env.example` | Runtime configuration template | No actual provider variables | Improve for optional Tavily and bounds |
| `app.py` | HTTP entry point, embedded browser UI, API/form handlers | Working v0.2; few scenarios and `/health` only | Improve; preserve route compatibility |
| `careershield/__init__.py` | Package marker | Minimal | Keep |
| `careershield/agent.py` | Baseline rules, score, trace and report | Deterministic checks, no actual registry/orchestration | Replace with bounded orchestrator and schema v2 |
| `tests/test_agent.py` | Original rule regressions | Seven direct unit cases | Improve and retain compatibility coverage |
| `tests/test_http.py` | Original HTTP integration tests | Five local HTTP cases | Improve; retain and run |
| `requirements.txt` | Dependency declaration | Standard library only | Keep; clarify runtime |
| `README.md` | Setup and product overview | Correctly stated offline limitations, but outdated feature list | Replace with exact v2 setup/status |
| `docs/DEMO_SCRIPT.md` | Hackathon demo flow | Described baseline features | Replace with executable v2 demo |
| `docs/HACKATHON_SCORECARD.md` | Judge-preparation checklist | Generic checklist, stale future-tool statements | Keep as supplementary checklist; align wording |
| `docs/MASTER_BUILD_PROMPT.md` | Duplicate of root upgrade prompt | Redundant, non-runtime prompt copy | Exclude from release; root copy retained |
| `docs/ROADMAP.md` | Feature status and future work | Said live web search and loop were not implemented | Replace with true status matrix |
| `docs/PRIVACY.md` | Privacy notes | Described no external search as unconditional | Replace with provider-specific data flow |
| `docs/THREAT_MODEL.md` | Threats and mitigations | Baseline gaps and proposed mitigations | Replace with implemented controls and residual risks |
| `docs/` (new `API.md`, `ARCHITECTURE.md`, `JUDGING_GUIDE.md`) | Operational and product documentation | Missing API/architecture/judging detail | Add |
| `samples/sample_cases.json` | Synthetic demonstration inputs | Three original examples | Keep and use in demo context |
| `evidence/ARCHITECTURE.md` | Baseline architecture narrative | Duplicate, stale view of original | Replace with concise pointer to current architecture |
| `evidence/TEST_EVIDENCE.md` | Prior test summary | Correct for baseline only | Replace with actual v2 result and limits |
| `evidence/TEST_RUN_OUTPUT.txt` | Prior original test output | Authentic baseline output | Replace with final v2 output |
| `evidence/example_suspicious_report.json` | Synthetic baseline result | Schema v1 | Regenerate from v2 code |
| `evidence/example_lower_signal_report.json` | Synthetic baseline result | Schema v1 | Regenerate from v2 code |
| `evidence/FAILURE_CASES.md` | Edge-case notes | Included known negation gaps | Update with tested behavior and residuals |
| `evidence/IMPLEMENTATION_NOTES.md` | Hackathon submission notes | Generic third-party event and baseline summary | Replace with truthful v2 implementation notes |
| `.github/workflows/tests.yml` | CI test workflow | Python 3.11–3.13 unittest matrix | Improve to include Python 3.10; run command matches project |
| `.dockerignore` | Docker context exclusions | Excluded caches/secrets | Improve if needed; retain useful rules |
| `Dockerfile` | Container packaging | Slim image, non-root UID, health check | Keep; not run in this environment |
| `docker-compose.yml` | Local container launch | Host port loopback mapping | Keep; docs note container path is optional |

The original archive contained no runtime binaries or local credentials. Python bytecode/cache files visible in the working tree were generated by verification and are excluded from the release.
