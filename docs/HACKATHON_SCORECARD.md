# Hackathon judge checklist

Use this to prepare a demo; it is not an official organizer rubric.

| Dimension | Demo evidence |
|---|---|
| Problem and impact | Student-facing payment/credential safety flow and practical independent-verification steps |
| Agent behavior | Input-sensitive registered checks, status/result trace, finite plan, and tested call/time stop conditions |
| Technical depth | Small standard-library application, stable API schema, deterministic offline fallback, and optional provider adapter |
| Trust | Concrete message snippets, coverage, uncertainty, source provenance, counter-evidence, and human review |
| Product quality | Responsive accessible form, seven synthetic scenario buttons, findings dashboard, source view, JSON download |
| Reliability | Real test output from the package, 40 synthetic cases, provider mocks, and actual local HTTP smoke test |
| Responsible implementation | No URL fetching, no automatic contact, no hidden persistence, no probability/accuracy claims |

Do not claim real-world detection performance from synthetic fixtures. Do not claim live provider verification unless a real credential was configured and a real response was reviewed. Keep the offline path available for judges.
