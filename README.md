# CareerShield AI — Enterprise-minded MVP

**Verify the evidence before you trust the offer.** CareerShield helps students and early-career applicants screen job and internship messages for warning signs, understand what was actually checked, and choose safe next steps.

This is an offline-first, evidence-aware screening tool. It does not decide that a person or company committed fraud. The score is a deterministic heuristic, not a probability. Human review is always required.

## Quick start

Requirements: Python 3.10 or newer. Runtime and tests use only the Python standard library; there are no pip dependencies.

Windows PowerShell:

```powershell
cd CareerShield-AI
python app.py
```

macOS/Linux:

```sh
cd CareerShield-AI
python3 app.py
```

Open <http://127.0.0.1:8000>. The server binds to loopback by default. Use one of the seven synthetic scenario buttons to demonstrate the full offline workflow. Stop with `Ctrl+C`.

Run all automated checks:

```sh
python -m unittest discover -s tests -v
```

No keys or network access are needed for the local app, scenarios, or standard test suite.

## Optional live search

The optional official-source discovery tool uses the Tavily Search API. It sends the company name and the fixed query suffix `official website careers`; it does not send the recruiter email, submitted URL, or offer text. Returned pages are source candidates only and are not proof that a recruiter or offer is genuine. User-submitted job URLs are never fetched.

Set `TAVILY_API_KEY` in the process environment to enable it. On Windows PowerShell:

```powershell
$env:TAVILY_API_KEY = 'your-real-key'
python app.py
```

macOS/Linux:

```sh
export TAVILY_API_KEY='your-real-key'
python3 app.py
```

Without a key, `/ready` reports `live_search: not_configured` and local checks still work. Provider failures do not create citations. Do not put real credentials in source files or reports. See [.env.example](.env.example).

## Product flow and built-in scenarios

The browser form accepts a company, recruiter email, job URL, job text, and optional region. The bounded orchestrator selects only registered checks relevant to supplied fields, records status and observable results, stops within configured call/time budgets, and creates a versioned report. The UI includes suspicious, lower-signal, ambiguous, incomplete, legitimate ATS, domain mismatch, and prompt-injection examples.

Local tools inspect payment language, credential requests, urgency/guaranteed-selection language, role-detail completeness, email syntax/domain type, URL structure, and email/URL consistency. Results are explainable and coverage-aware. Local checks do not browse, resolve, or fetch a submitted URL.

## API

- `GET /` and `/index.html`: browser application.
- `GET /health`: liveness and application version.
- `GET /ready`: readiness of local tools and whether live search is configured; never reveals credentials.
- `POST /api/v1/analyze`: JSON request and version 2 report.
- `POST /analyze`: URL-encoded browser route retained for compatibility.

See [docs/API.md](docs/API.md) for schemas and error examples. Request body is limited to 30,000 bytes and individual fields have limits. No CORS allow-origin header is enabled. Analysis content is processed in memory and is not persisted by default.

## Features and status

| Feature | Status |
|---|---|
| Offline deterministic checks, scoring, report, and responsive browser UI | **Implemented and tested** |
| Registered bounded plan/act/observe/decide/finalize loop and prompt-injection-as-data handling | **Implemented and tested** |
| Tavily official-source discovery adapter | **Implemented, integration not configured** until a real API key is set |
| Mocked provider success/failure and provenance contract tests | **Mocked in automated tests only** |
| LLM extraction/summarization, URL reputation, company registry/ownership checks, user accounts/history | **Planned / future work** |

See [docs/ROADMAP.md](docs/ROADMAP.md) for full boundaries and [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) for residual risks.

## Docker (optional)

Docker assets use a slim Python image, non-root UID, health check, and loopback host mapping. Docker was not required for the clean-extraction verification; use it only if Docker Engine and Compose are installed:

```sh
docker compose up --build
```

Open <http://127.0.0.1:8000>. The container listens on its internal interface while Compose publishes only to host loopback. A production or shared deployment needs additional controls described in the threat model.

## Project map

- `app.py`: standard-library HTTP server and browser UI.
- `careershield/agent.py`: bounded orchestration, scoring, report assembly.
- `careershield/tools.py`: deterministic tools and optional Tavily adapter.
- `tests/`: unit, provider-contract, HTTP, and fixture evaluation tests.
- `samples/evaluation_cases.json`: 40 synthetic cases; not a real-world benchmark.
- `docs/`: API, architecture, privacy, security, demo, judging, roadmap.
- `evidence/`: original archive audit, actual test output, sample reports, and verification notes.

## Safety and limitations

Do not submit passwords, OTPs, PINs, CVV codes, bank login details, government IDs, or unrelated personal information. A personal email, ATS domain, unfamiliar company, urgency term, non-HTTPS URL, domain mismatch, or low score is not proof of fraud or legitimacy. The optional search provider shares only a company name with Tavily. The app does not provide authentication, rate limiting, user accounts, persistent history, verified identity/company ownership, URL reputation, or a calibrated real-world accuracy estimate. It is an MVP, not a production-ready security service.
