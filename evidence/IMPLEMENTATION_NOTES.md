# Implementation notes

CareerShield v2 remains a dependency-free Python application. The HTTP server enforces request and field limits; a single bounded orchestrator selects registered local tools based on supplied input, records observations and produces a stable schema-v2 JSON report. An optional Tavily adapter can discover public source candidates when explicitly configured. This package was exercised without a provider credential, so its live search status remains not configured.

The local checks are deterministic heuristics, not an LLM, fraud classifier, or calibrated probability. The app never fetches a submitted URL, stores submitted messages, contacts a recruiter, or makes an irreversible external action. Provider failure leaves the local report usable and does not create a citation.

For exact setup/API/test commands, see the project README and `docs/API.md`. The final test command/output and package verification are recorded in `TEST_EVIDENCE.md` and `TEST_RUN_OUTPUT.txt`. The synthetic dataset is not a real-world benchmark.
