# Feature status and roadmap

| Feature | Status |
|---|---|
| Offline local checks, explainable heuristic, cautious report and JSON download | **Implemented and tested** |
| Input-sensitive tool routing, bounded registry, observable trace and stop conditions | **Implemented and tested** |
| Body/field validation, security headers, health/readiness endpoints and legacy route | **Implemented and tested** |
| Seven offline synthetic UI scenarios and 40 synthetic regression cases | **Implemented and tested** |
| Submitted URL structure analysis without fetching | **Implemented and tested** |
| Tavily company/careers source discovery adapter | **Implemented, integration not configured** until user supplies a real API key; no external call was made for the packaged verification |
| Tavily successful/malformed response contracts and source provenance | **Mocked in automated tests only** |
| LLM extraction or summarization | **Planned / future work** |
| URL reputation service and company/recruiter identity verification | **Planned / future work** |
| Authentication, public deployment rate limiting, accounts, persistent history and deletion controls | **Planned / future work** |
| Calibrated risk probabilities or accuracy claims | **Planned / future work**; requires representative labeled data and validation |

## Next work

1. Configure a real search credential in a controlled environment and review source freshness, provider terms, and evidence usefulness.
2. Add authentic source comparison and contradiction extraction only when the source evidence supports it; keep identity verification limits explicit.
3. Add deployment controls before exposing the server to multiple users.
4. If an LLM is later added, constrain it to structured extraction/summarization of supplied evidence and prove its output cannot select tools or alter safety rules.
5. Build a representative, consented evaluation set before presenting any real-world performance metric.

The current package is an improved hackathon MVP, not a production-ready security product.
