# Three-minute offline demo

## Prepare

From a clean extraction, run `python app.py` (Windows) or `python3 app.py` (macOS/Linux), then open `http://127.0.0.1:8000`. No API key or internet is required. All click-to-fill examples are synthetic.

## Walkthrough

### 0:00–0:20 — Student safety problem

Explain: job messages can ask for money or authentication details. CareerShield identifies text-based warning signs and points users to independent checks; it does not label a company or sender as fraudulent.

### 0:20–1:05 — High-concern example

Click **Suspicious**, then **Analyze offer**. Point to the actual payment/OTP snippets, the conditional tools that ran, capped heuristic score, and advice not to pay or share secrets. Mention that the URL was parsed but never fetched.

### 1:05–1:40 — Tool routing and limits

Show the coverage and investigation timeline: input-driven plan, named allowlisted checks, observed match counts, and stop reason. Run an input with only a URL to show text tools are skipped/not planned. The trace explains observable actions, not hidden chain-of-thought.

### 1:40–2:10 — Ambiguity and fair handling

Click **Ambiguous** or **Incomplete**. Show missing information and the `Needs more information` state. Click **Legitimate ATS** to show a recognized hiring platform is not automatically called suspicious. A personal email by itself adds context, not proof.

### 2:10–2:35 — Untrusted content

Click **Prompt injection**. Explain that the message is treated as data: no LLM is running, and it cannot add tools or trigger external actions. Click **Domain mismatch** to show a review signal rather than an accusation.

### 2:35–3:00 — Reproducibility and limits

Run `python -m unittest discover -s tests -v`. Explain the 40-case synthetic suite and the local HTTP smoke checks. State that no live provider credential was used in the packaged run, no company/recruiter identity is verified, and the score is not a probability.

## Example request

```json
{
  "company_name": "Example Technologies",
  "recruiter_email": "recruiter@gmail.com",
  "job_url": "http://bit.ly/example-job",
  "job_text": "Guaranteed selection without interview. Pay a registration fee. Send your OTP."
}
```

If the browser is unavailable, use `GET /health`, `GET /ready`, and `POST /api/v1/analyze`. The standard test suite is the offline backup.
