# Final test and smoke evidence

## Automated suite

- Command: `python -m unittest discover -s tests -v`
- Runtime: CPython 3.13.9, Windows, Python standard-library only.
- Result: **37 tests passed, 0 failed, 0 skipped**. Actual working-tree output is in `TEST_RUN_OUTPUT.txt`; output from the first extraction of the built ZIP is in `CLEAN_EXTRACTION_TEST_OUTPUT.txt`.
- Synthetic evaluation: 40 explicitly labeled synthetic fixtures were executed by one fixture-loop test; all expected/forbidden indicator assertions passed. These are not real-world accuracy results.
- HTTP tests use a local loopback test server and cover the browser page, security headers, readiness without secret disclosure, versioned JSON API, legacy form API, malformed and unsupported requests, type/size errors, and reports.
- Provider tests mock Tavily responses, including returned-source provenance, empty result, malformed response, timeout, and rate limit. No external search call or real API credential was used in this package verification.

## Actual application smoke test

Started `python app.py` as a separate process and made HTTP requests to `/`, `/health`, `/ready`, and `/api/v1/analyze`. The page returned HTTP 200 and contained the product tagline; liveness/readiness returned `ok`/`ready`; the sample payment and OTP message returned HTTP 200 with `High` and both corresponding findings. The process was stopped after the checks.

## Baseline comparison

The untouched source ZIP was independently re-extracted and its original test command ran **12 tests, all passed** after local socket permission was available. `BASELINE_TEST_RUN_OUTPUT.txt` preserves that output. The initial restricted-sandbox attempt had five HTTP errors because Windows denied localhost sockets; those were environment errors and not counted as application failures.

## Limits

The tests use deterministic synthetic inputs and mocks; they do not measure real-world screening accuracy, authenticate an employer/recruiter, verify a job vacancy, or constitute a security assessment. Docker was not verified in this environment. The optional Tavily integration remains unconfigured.
