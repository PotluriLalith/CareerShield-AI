# Changelog

## 2.0.0 — Enterprise-minded MVP

- Added a registered, conditional investigation tool loop with call, deadline, and response-size bounds.
- Added deterministic checks for recruitment payment and credential requests, urgency/guaranteed selection, job detail coverage, email domain, URL structure, and ATS-aware domain consistency.
- Added an optional Tavily official-source discovery adapter with source metadata, disabled by default and never used as identity proof.
- Versioned the report to schema 2.0 with findings, verification status, coverage, sources, tool statuses, counter-evidence, missing data, recommendations, and human-review requirement. Retained legacy report aliases and `/analyze`.
- Added readiness endpoint, seven offline UI scenarios, accessible result rendering, and explicit score/source limitations.
- Added 40 synthetic evaluation fixtures, provider contract tests, agent budget/routing tests, HTTP checks, updated threat/privacy/API/docs, and truthful evidence.
- Preserved the standard-library runtime and loopback default. No LLM, URL fetcher, persistent history, or production authentication was added.
