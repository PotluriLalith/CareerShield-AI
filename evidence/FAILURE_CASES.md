# Failure cases and tested boundaries

| Case | Current behavior | Remaining limitation |
|---|---|---|
| No useful input | `Needs more information`, no score, missing fields listed | Cannot assess facts that were not supplied |
| Explicit negated/quoted payment example | Excluded by local checks and covered by regression tests | English context and complex quotations remain imperfect |
| OTP/password/PIN/bank credential request | High-severity local signal and protective next step | Pattern checks can miss paraphrases or misunderstand quoted context |
| Personal email | Zero-point context item; not a fraud claim | No recruiter ownership verification |
| Recognized ATS host | Not treated as a mismatch by itself | ATS allowlist is finite and can become stale |
| Unknown email/URL domain difference | Review signal with explanation; not proof | Legitimate recruiting arrangements can differ |
| Raw IP, user-info, punycode, IDN, shortener, or HTTP URL | Structural caution; URL is never opened | No redirect, destination, reputation, or ownership check |
| Prompt injection in message | Remains untrusted text; it cannot add tools; no LLM exists | This is not a claim of LLM-injection protection for future models |
| Missing Tavily key / malformed provider response | Local checks continue; no source fabricated | Live discovery requires a real credential and provider availability |
| Conflicting live sources | No automated conflict resolution currently exists; no sources are ranked as proof | Human must compare returned source candidates |
| Highly polished but deceptive offer | May yield a low score | Local heuristics are incomplete and not validated for real-world accuracy |
| Public/shared deployment | Not supported as-is | No auth, rate limit, tenant isolation, TLS termination, or operations controls |

All included evaluation examples are synthetic and only test expected code behavior. They do not estimate production accuracy.
