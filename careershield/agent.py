"""Bounded plan-act-observe-decide-finalize screening orchestrator."""
from __future__ import annotations

from datetime import datetime, timezone
import os
import re
import math
import uuid
from typing import Any

from .tools import ToolRegistry, ToolResult

AGENT_NAME = "CareerShield AI"
AGENT_VERSION = "2.0.0"
REPORT_SCHEMA_VERSION = "2.0"
SCORING_VERSION = "1.0"


def _env_number(name: str, default: float) -> float:
    try:
        value = float(os.environ.get(name, str(default)))
        return value if math.isfinite(value) else default
    except ValueError:
        return default


MAX_TOOL_CALLS = int(_env_number("CAREERSHIELD_MAX_TOOL_CALLS", 8))
TOOL_TIMEOUT_SECONDS = _env_number("CAREERSHIELD_TOOL_TIMEOUT_SECONDS", 4)
MAX_DURATION_SECONDS = _env_number("CAREERSHIELD_MAX_DURATION_SECONDS", 15)


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _safe_snippet(value: str) -> str:
    """Keep evidence concise and avoid echoing likely authentication values."""
    safe = value[:260]
    safe = re.sub(r"(?i)\b(otp|one[- ]time password|passcode|password|pin|cvv)\b\s*(?:is|:|=|code)?\s*[A-Za-z0-9-]{3,}", r"\1 [redacted]", safe)
    safe = re.sub(r"\b\d{4,}\b", "[redacted number]", safe)
    return safe


def _finding(code: str, title: str, severity: str, snippet: str, explanation: str,
             tool: str, points: int, classification: str = "heuristic_indicator") -> dict[str, Any]:
    safe = _safe_snippet(snippet)
    return {"code": code, "title": title, "severity": severity, "evidence_snippet": safe,
            "evidence": (explanation + " Evidence: " + safe)[:520], "explanation": explanation, "tool": tool,
            "provenance": "user_submitted_text" if classification == "heuristic_indicator" else "local_input_inspection",
            "observed_at": _stamp(), "score_contribution": points, "points": points,
            "classification": classification}


def investigate_offer(payload: dict[str, str], registry: ToolRegistry | None = None) -> dict[str, Any]:
    """Inspect provided details locally and optionally discover public official sources.

    Submitted text is always treated as data. The only outbound tool is an optional,
    allowlisted provider search; a user-supplied URL is structurally inspected only.
    """
    company = payload.get("company_name", "").strip()
    email = payload.get("recruiter_email", "").strip()
    job_url = payload.get("job_url", "").strip()
    text = payload.get("job_text", "").strip()
    region = payload.get("region", "").strip()
    reg = registry or ToolRegistry(MAX_TOOL_CALLS, TOOL_TIMEOUT_SECONDS, MAX_DURATION_SECONDS)
    plan: list[tuple[str, str, str]] = []
    if text:
        plan.extend([
            ("payment_language_detector", text, "Offer text was supplied; check for money-transfer or recruitment-fee language."),
            ("credential_request_detector", text, "Offer text was supplied; check for credentials or authentication codes."),
            ("urgency_claim_detector", text, "Offer text was supplied; check for time pressure and guaranteed-selection claims."),
            ("role_completeness_checker", text, "Offer text was supplied; assess whether role responsibilities and requirements are described."),
        ])
    if email:
        plan.append(("email_domain_inspector", email, "A recruiter email was supplied; inspect syntax and domain type."))
    if job_url:
        plan.append(("url_structure_inspector", job_url, "A job URL was supplied; inspect URL syntax and hostname without fetching it."))
    if company and os.environ.get("TAVILY_API_KEY", "").strip():
        plan.append(("official_source_search", company, "A company name was supplied and live search is configured; discover public official-source candidates."))

    trace: list[dict[str, Any]] = [{"stage": "plan", "reason": f"Planned {len(plan)} relevant check(s) from the supplied fields; no user-supplied URL will be fetched."}]
    observed: dict[str, ToolResult] = {}
    tools_used: list[dict[str, Any]] = []
    for name, value, reason in plan:
        result = reg.run(name, value)
        observed[name] = result
        tools_used.append({"tool_name": name, "name": name, "selection_reason": reason, "status": result.status,
                           "duration_ms": result.duration_ms, "result_summary": result.summary,
                           "provider": result.provider})
        trace.append({"stage": "act_observe", "tool": name, "reason": reason,
                      "observation": result.summary, "status": result.status})
        if result.status in {"not_configured", "unavailable", "failed", "timed_out", "rate_limited", "completed_no_results"}:
            trace.append({"stage": "decide", "reason": f"{name} returned {result.status}; retained local-only conclusions and did not retry."})

    findings: list[dict[str, Any]] = []
    score = 0
    def add(code: str, title: str, severity: str, snippet: str, explanation: str, tool: str, points: int) -> None:
        nonlocal score
        if any(item["code"] == code for item in findings):
            return
        findings.append(_finding(code, title, severity, snippet, explanation, tool, points))
        score += points

    matches = observed.get("payment_language_detector")
    if matches and matches.data.get("matches"):
        add("payment_request", "Payment or transfer language", "high", matches.data["matches"][0],
            "This passage appears to request money or a payment method. Do not pay until independently confirmed through official company channels.", "payment_language_detector", 35)
    matches = observed.get("credential_request_detector")
    if matches and matches.data.get("matches"):
        add("credential_request", "Sensitive credential request", "critical", matches.data["matches"][0],
            "The passage appears to request an authentication code or account credential. Do not share OTPs, passwords, PINs, CVV codes, or bank logins.", "credential_request_detector", 55)
    matches = observed.get("urgency_claim_detector")
    if matches and matches.data.get("matches"):
        add("urgency", "Urgency or guaranteed-selection wording", "medium", matches.data["matches"][0],
            "This wording applies time pressure or suggests guaranteed selection. It needs context and is not proof of fraud.", "urgency_claim_detector", 12)
        if "without interview" in text.lower() or "no interview" in text.lower():
            findings.append(_finding("instant_offer", "Guaranteed selection without an interview", "medium", matches.data["matches"][0],
                                     "Guaranteed selection without an interview warrants review but is not proof of fraud.", "urgency_claim_detector", 0))

    email_data = observed.get("email_domain_inspector")
    url_data = observed.get("url_structure_inspector")
    email_host = email_data.data.get("domain") if email_data else None
    url_host = url_data.data.get("hostname") if url_data else None
    if email and email_data and not email_data.data.get("valid"):
        add("invalid_email", "Recruiter email could not be parsed", "low", email[:180], "Check the address carefully; its ownership has not been verified.", "email_domain_inspector", 5)
    elif email_data and email_data.data.get("personal_provider"):
        findings.append(_finding("personal_email", "Personal email provider", "info", email_host or "", "Personal email can occur in legitimate hiring; this is context only, not proof of fraud.", "email_domain_inspector", 0))
    if job_url and url_data and not url_data.data.get("valid"):
        add("unparseable_url", "URL could not be safely parsed", "medium", job_url[:180], "The URL could not be interpreted as a normal HTTP(S) address; verify it manually through the official website.", "url_structure_inspector", 8)
    elif url_data:
        for obs in url_data.data.get("observations", []):
            if obs == "URL uses a known shortener":
                add("shortened_url", "Shortened link hides its destination", "medium", url_host or "", "Confirm the destination through an independently located company website before opening.", "url_structure_inspector", 10)
            elif obs == "URL uses a raw IP address":
                add("ip_url", "URL uses a raw IP address", "medium", url_host or "", "A raw IP URL deserves careful review; it does not establish who controls it.", "url_structure_inspector", 10)
            elif obs.startswith("URL contains embedded") or "punycode" in obs or "internationalized" in obs:
                add("url_lookalike", "URL hostname needs careful review", "medium", obs, "Review the displayed hostname and use the company's official site independently.", "url_structure_inspector", 10)
            elif obs == "URL does not use HTTPS":
                add("non_https", "URL does not use HTTPS", "low", job_url[:180], "This is one caution signal and is not proof of fraud. Verify using the official website.", "url_structure_inspector", 5)

    if email_host and url_host:
        platforms = ("greenhouse.io", "lever.co", "myworkdayjobs.com", "workday.com", "ashbyhq.com", "smartrecruiters.com", "icims.com", "jobvite.com", "taleo.net")
        platform = any(url_host == d or url_host.endswith("." + d) for d in platforms)
        email_platform = any(email_host == d or email_host.endswith("." + d) for d in platforms)
        if not platform and not email_platform and email_host != url_host and not email_host.endswith("." + url_host) and not url_host.endswith("." + email_host):
            add("domain_mismatch", "Recruiter email and URL domains differ", "medium", f"Email domain: {email_host}; URL domain: {url_host}.",
                "The supplied domains differ. This is not proof of fraud: hiring platforms and recruitment arrangements can explain it. Verify from the company's official careers page.", "domain_consistency_check", 12)

    role = observed.get("role_completeness_checker")
    if role and role.data.get("complete_dimensions", 0) == 0 and text:
        findings.append(_finding("limited_role_detail", "Role details are limited", "info", text[:220], "Few common responsibility, qualification, or role details were detected. Missing detail lowers coverage; it does not prove fraud.", "role_completeness_checker", 0))

    sources: list[dict[str, Any]] = []
    search_result = observed.get("official_source_search")
    if search_result:
        sources = search_result.data.get("sources", [])[:4]
    info_count = sum(bool(v) for v in (company, email, job_url, text))
    enough = info_count >= 2 and bool(text or job_url)
    score = min(score, 100)
    sparse_role = bool(text and role and role.data.get("complete_dimensions", 0) == 0)
    risk = "Needs more information" if not enough else "High" if score >= 50 else "Medium" if score >= 25 else "Needs review" if sparse_role else "Low"
    assessment = "incomplete" if not enough else "complete with limitations"
    if not enough:
        summary = "There is not enough information to assess this offer. Add the message and at least one useful company, recruiter, or URL detail."
    elif risk == "High":
        summary = "High-severity warning signs were found in the supplied details. Pause and verify through an independently located official company channel before taking action."
    elif risk == "Medium":
        summary = "Some warning signs need review. Verify the recruiter and role independently before sharing information or proceeding."
    elif risk == "Needs review":
        summary = "The message contains too little role detail for a useful screen. Request the full job description and verify through an independently located official channel."
    else:
        summary = "Few warning patterns were detected in the supplied details. This does not prove the offer is genuine; independent verification is still required."

    missing = [label for key, label in (("company_name", "Company name"), ("recruiter_email", "Recruiter email"), ("job_url", "Official company careers page or job URL"), ("job_text", "Full job offer/message text")) if not payload.get(key, "").strip()]
    counter_evidence = []
    if text and not (observed.get("payment_language_detector") and observed["payment_language_detector"].data.get("matches")):
        counter_evidence.append("No payment request was detected by the local language check; this does not establish safety.")
    if text and not (observed.get("credential_request_detector") and observed["credential_request_detector"].data.get("matches")):
        counter_evidence.append("No credential request was detected by the local language check; this does not establish safety.")
    if role and role.data.get("complete_dimensions", 0) >= 2:
        counter_evidence.append("The supplied text includes some commonly expected role details; those details were not independently verified.")
    next_steps = []
    if any(f["code"] in {"payment_request", "credential_request"} for f in findings):
        next_steps.append("Do not pay recruitment fees or share OTPs, passwords, PINs, CVV codes, or bank login details.")
    next_steps.extend(["Find the company's official website independently and compare the vacancy and recruiter contact details there.",
                       "Contact the company through a phone number or email published on its official website, not only through the message you received."])
    if missing:
        next_steps.append("Add the missing details to improve screening coverage: " + ", ".join(missing) + ".")
    next_steps.append("Treat this result as a preliminary screen; a person must make the final decision after independent checks.")

    sources_status = "sources_found" if sources else "not_attempted"
    live_status = search_result.status if search_result else "not_configured"
    coverage = {"available_fields": [k for k, v in (("company_name", company), ("recruiter_email", email), ("job_url", job_url), ("job_text", text), ("region", region)) if v],
                "checks_planned": len(plan), "checks_completed": sum(1 for t in tools_used if t["status"] == "completed"),
                "tool_call_budget": reg.max_calls, "tool_calls_used": reg.calls, "live_search_status": live_status}
    trace.append({"stage": "decide", "reason": "No further useful distinct local check remains; investigation stopped within the configured call budget."})
    trace.append({"stage": "finalize", "reason": "Final report combines observed local indicators and provider-returned sources only; no source or verification result was inferred."})
    report = {
        "agent_name": AGENT_NAME, "agent_version": AGENT_VERSION, "report_schema_version": REPORT_SCHEMA_VERSION,
        "schema_version": REPORT_SCHEMA_VERSION, "report_id": "csr_" + uuid.uuid4().hex[:12], "generated_at": _stamp(),
        "assessment_status": assessment, "risk_level": risk, "heuristic_score": score if enough else None,
        "score": score if enough else None, "score_methodology_version": SCORING_VERSION,
        "scoring_method": "Version 1.0 additive deterministic heuristic, capped at 100. Not a probability or fraud verdict.",
        "verification_status": "sources_found" if sources else "local_only", "summary": summary,
        "confidence": "Limited — supplied details only; external ownership is unverified",
        "findings": findings, "signals": findings,
        "sources": sources,
        "tools_used": tools_used, "checks": [{"tool": x["tool_name"], "status": x["status"], "detail": x["result_summary"]} for x in tools_used],
        "coverage": coverage, "counter_evidence": counter_evidence, "contradictions": [],
        "missing_information": missing, "recommended_next_steps": next_steps, "recommendations": next_steps,
        "execution_trace": trace, "limitations": [
            "Local deterministic screening is a preliminary aid, not a calibrated risk model.",
            "User-supplied job URLs are structurally inspected only and are never fetched.",
            "Company identity, recruiter ownership, vacancy authenticity, and company registration are not verified.",
            "A source discovery result, if present, is a candidate for human review and does not authenticate an offer or sender.",
            "A low score does not prove an offer is genuine; a high score is not a definitive fraud finding.",
            "Offer content is processed in memory and is not persisted by default."
        ],
        "human_review_required": True,
        "input_summary": {"company_name_provided": bool(company), "recruiter_email_provided": bool(email),
                          "job_url_provided": bool(job_url), "job_text_provided": bool(text), "region_provided": bool(region)},
    }
    if not sources:
        report["limitations"].append("This run did not browse the live web because no source results were available; local checks only are shown.")
    return report
