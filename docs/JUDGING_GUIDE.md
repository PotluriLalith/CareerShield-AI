# Judging guide

## Problem and user value

Students and early-career applicants often need to evaluate an offer with limited context. The product helps them recognize specific risky requests, see which checks ran, and take independent verification steps.

## Differentiation to demonstrate

- The application routes to small registered tools based on fields actually supplied and returns an observable plan/action/result/stop trace.
- It shows exact supporting snippets, missing details, counter-evidence, coverage, source status, and safe recommendations.
- It treats a score as a heuristic, keeps a personal email/ATS domain from becoming a fraud verdict, and requires human review.
- The local demo works without credentials or internet. With a real `TAVILY_API_KEY`, the optional adapter can discover public pages and preserves returned source metadata; the adapter is tested with mocks in this release.
- User-supplied URLs are never fetched, and message text cannot add tools or trigger external actions.

## What the evidence proves

The packaged test run covers the 37 automated tests and 40 synthetic text cases in `samples/evaluation_cases.json`; provider interactions are mocked. HTTP smoke checks were run against the actual app. This proves only the listed code paths on synthetic examples. It does not establish real-world precision/recall, authenticate companies or recruiters, prove provider accuracy, or constitute a security audit.

## Suggested demo

Use [the timed demo script](DEMO_SCRIPT.md): suspicious payment/OTP request, tool trace, ambiguous/incomplete offer, ATS example, domain mismatch, prompt injection case, then test evidence and limitations. No credentials are needed.
