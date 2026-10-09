# HTTP API

All routes are served by `python app.py` at `http://127.0.0.1:8000`. CORS is not enabled. JSON responses are UTF-8 and include conservative browser security headers.

## `GET /health`

Liveness response. Example: `{"status":"ok","service":"CareerShield AI","version":"2.0.0","mode":"local-rule-based-demo"}`.

## `GET /ready`

Reports local tool readiness and live-search configuration without returning a key, e.g. `{"status":"ready","version":"2.0.0","local_tools":"available","live_search":"not_configured"}`.

## `POST /api/v1/analyze`

Content type: `application/json`. Unknown fields are ignored. Supported request:

```json
{
  "company_name": "Example Technologies",
  "recruiter_email": "recruiter@example.com",
  "job_url": "https://careers.example.com/role",
  "job_text": "Software engineering intern role...",
  "region": "India"
}
```

All fields are optional strings. Limits: body 30,000 bytes; company 300 characters; email 320; URL 2,000; job text 20,000; region 120. The form route `POST /analyze` accepts the same fields as `application/x-www-form-urlencoded` and returns the same report.

The schema v2 response includes `report_id`, `generated_at`, `agent_version`, `schema_version`, `assessment_status`, `risk_level`, nullable `heuristic_score`, `score_methodology_version`, `verification_status`, `coverage`, `summary`, `findings[]`, `sources[]`, `tools_used[]`, `missing_information[]`, `contradictions[]`, `counter_evidence[]`, `recommended_next_steps[]`, `limitations[]`, `human_review_required`, `input_summary`, plus compatibility aliases `signals`, `checks`, `score`, and `recommendations`.

Each finding includes stable `code`, `title`, `severity`, `evidence_snippet`, `explanation`, `tool`, `provenance`, `observed_at`, `score_contribution`, and `classification`. Classifications include `heuristic_indicator`; a source candidate is carried separately in `sources[]` and is not treated as verification of identity.

## Error responses

Errors use a small JSON object such as `{"error":"Field 'company_name' must be a string."}`.

| Status | Condition |
|---|---|
| 400 | Empty body, malformed JSON/form, non-object JSON, or a field that is not a string |
| 413 | Body or individual field exceeds its limit |
| 415 | Content type is not JSON or URL-encoded form |
| 404 | Unknown path |
| 500 | Unexpected analysis exception; internal details and submitted text are not returned |

Example request:

```sh
curl -s http://127.0.0.1:8000/api/v1/analyze \
  -H 'Content-Type: application/json' \
  -d '{"company_name":"Example","job_text":"Pay a registration fee now."}'
```

The score is a deterministic, capped heuristic and must not be interpreted as a probability. Missing information reduces coverage; it does not itself raise the score. Clients should display `limitations`, `verification_status`, and `human_review_required` alongside the risk label.
