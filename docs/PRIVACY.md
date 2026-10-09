# Privacy and data handling

## Inputs and processing

The app accepts company name, recruiter email, job URL, job text, and optional region. It validates and analyzes these fields in process memory. It does not write submissions or reports to a database, filesystem history, or analytics service. The response may contain short evidence snippets derived from submitted text so users can understand a finding; the application does not echo the full text as an input field in the report.

Do not submit passwords, OTPs, PINs, CVV values, bank login details, government IDs, or unrelated personal information. This tool is not a secure document-storage or identity-verification service.

## Network sharing

The default offline run makes no external request. If `TAVILY_API_KEY` is configured, the optional official-source discovery call sends Tavily the company name and a fixed `official website careers` query. It does not send recruiter email, submitted URL, offer text, or region. Tavily returns source candidates that the app includes with retrieval metadata; they are not treated as verified facts. Consult the provider's current terms/privacy notice before enabling it.

The application never fetches a user-supplied job URL. There is no LLM adapter, URL reputation service, or external contact action.

## Logs, retention, deletion

The local HTTP server logs request path, status, and normal server metadata, not request bodies. Submissions exist in process memory for the duration of a request and in the browser until the user clears the form/page. Downloaded JSON is saved only after the user chooses the download button and is the user's responsibility to store/delete. There is no server-side history or retention job.

## Deployment

The app binds to loopback by default. A multi-user deployment changes the exposure and privacy context and requires authentication, transport security, retention/deletion controls, access logging policy, provider disclosure/consent, abuse protections, and a reviewed privacy notice. No regulatory compliance or certification is claimed.
