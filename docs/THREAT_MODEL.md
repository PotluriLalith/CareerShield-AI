# Threat model

## Assets and trust boundaries

Assets include submitted offer text, contact details, report integrity, and the optional Tavily API key. Browser/API input, job content, and search results are untrusted. The process is local by default; the optional provider boundary receives only a company name and fixed query.

## Threats and controls

| Threat | Implemented control | Residual risk |
|---|---|---|
| Oversized or malformed requests | 30 KB body ceiling, per-field ceilings, content-type/type validation, predictable JSON errors | No public-deployment rate limit or authenticated quota |
| XSS from user/provider data | Report values use DOM text nodes; source links require HTTPS and use `noopener noreferrer`; response headers include CSP, `nosniff`, frame denial | CSP permits inline script/style for the embedded UI; browser testing is not a security audit |
| SSRF through supplied job URLs | URL parser only; it never makes a request to a submitted URL | The optional search provider independently performs web search for company name; provider behavior is outside this app's network boundary |
| Prompt injection in job text or provider excerpts | No LLM is configured; content is treated as data; tools are a finite allowlist; tests include hostile text and tool-budget assertions | Rule detection can misclassify context; no LLM injection defense is claimed |
| Fabricated or overstated sources | Source objects are populated only from actual provider responses; URLs must be HTTPS; statuses say source discovery is not independent verification | Provider may return inaccurate or manipulated pages; a reviewer must inspect them |
| Secret leakage | Key is read from `TAVILY_API_KEY`; no secret is returned by `/ready`; `.env` is ignored; logs omit body fields | Host-level environment and process security remain the operator's responsibility |
| Privacy leakage | No database or history; analysis is in memory; request logs contain route/status, not submitted fields; provider receives only company name/query | The browser receives evidence snippets; users should redact sensitive details and avoid pasting secrets |
| False accusation or false reassurance | Heuristic disclaimer, cautious labels, evidence snippets, missing-data and counter-evidence sections, human review required | The simple deterministic rules are incomplete and are not validated against real-world outcomes |
| Denial of service | Body and tool-call/time/response limits; one pass per registered tool; no external user-URL fetch | Python standard-library HTTP server has no rate limiter, worker cap, or production-grade queue |

## Non-goals and deployment boundary

No authentication, authorization, tenant isolation, persistence, company registration checks, domain ownership checks, URL reputation, public crawler, automatic recruiter contact, or automated accusation is implemented. The local app is an MVP. A shared/public deployment needs TLS, authentication, rate limiting, concurrency controls, abuse monitoring, secret management, retention policy, incident response, dependency/image scanning, security review, and privacy/legal review appropriate to its jurisdiction. No certification or penetration test is claimed.
