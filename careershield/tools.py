"""Registered, bounded investigation tools. Submitted URLs are never fetched."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import os
import re
import socket
import time
from typing import Any, Callable
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit


@dataclass(frozen=True)
class ToolResult:
    name: str
    status: str
    summary: str
    data: dict[str, Any]
    duration_ms: int
    provider: str = "local"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _quoted_or_negated(text: str, start: int, end: int) -> bool:
    before = text[max(0, start - 90):start].lower()
    if re.search(r"\b(?:never|no|don't|do not|doesn't|won't|will not|should not|must not|cannot|can't)\b.{0,20}$", before):
        return True
    if re.search(r"\b(?:never|no|don't|do not|doesn't|won't|will not|should not|must not|cannot|can't)\b.{0,55}\b(?:charge|ask|request|require|pay|send|share|provide|buy)\b.{0,35}$", before):
        return True
    for left, right in ((text.rfind('"', 0, start), text.find('"', end)),
                        (text.rfind("“", 0, start), text.find("”", end))):
        if left >= 0 and right >= end:
            return True
    return False


def payment_language(text: str) -> dict[str, Any]:
    patterns = [r"\b(?:pay|payment|transfer|send|deposit)\b.{0,60}\b(?:fee|money|funds|cash|crypto|bitcoin|gift\s?cards?)\b",
                r"\b(?:registration|application|training|processing|security|equipment)\s+fee\b",
                r"\b(?:gift\s?cards?|cryptocurrency|bitcoin)\b"]
    matches = []
    for pattern in patterns:
        for m in re.finditer(pattern, text, re.I):
            start = max(0, m.start() - 45); end = min(len(text), m.end() + 45)
            snippet = text[start:end].strip()
            # Explicit policy negation is not a demand. Quoted examples are labeled as context.
            if _quoted_or_negated(text, m.start(), m.end()):
                continue
            if snippet not in matches:
                matches.append(snippet)
    return {"matches": matches[:5]}


def credential_language(text: str) -> dict[str, Any]:
    pattern = re.compile(r"\b(?:send|share|provide|reply with|submit|give us|confirm with)\b.{0,65}\b(?:otp|one[- ]time password|password|passcode|pin|cvv|bank login|online banking credentials)\b|\b(?:otp|password|pin|cvv|bank login)\b.{0,45}\b(?:send|share|provide|reply|submit)\b", re.I)
    matches = []
    for m in pattern.finditer(text):
        if _quoted_or_negated(text, m.start(), m.end()):
            continue
        matches.append(text[max(0,m.start()-45):min(len(text),m.end()+45)].strip())
        if len(matches) == 5:
            break
    return {"matches": matches}


def urgency_language(text: str) -> dict[str, Any]:
    patterns = [r"\b(?:act now|urgent|immediately|today only|limited slots|within \d+ hours?)\b",
                r"\b(?:guaranteed|instant)\b.{0,45}\b(?:job|selection|offer|hired)\b.{0,40}\b(?:without|no)\s+interview\b"]
    matches = []
    for p in patterns:
        for m in re.finditer(p, text, re.I):
            before = text[max(0,m.start()-35):m.start()].lower()
            if re.search(r"\b(?:not|never|isn't|is not)\b.{0,20}$", before):
                continue
            matches.append(text[max(0,m.start()-35):min(len(text),m.end()+35)].strip())
    return {"matches": matches[:5]}


def role_completeness(text: str) -> dict[str, Any]:
    lower = text.lower()
    dimensions = {"responsibilities": any(x in lower for x in ("responsibilit", "you will", "duties", "build", "develop", "support")),
                  "requirements": any(x in lower for x in ("requirements", "qualifications", "experience", "skills", "proficiency")),
                  "role_details": any(x in lower for x in ("intern", "engineer", "analyst", "designer", "manager", "developer", "role", "position"))}
    return {"dimensions": dimensions, "complete_dimensions": sum(dimensions.values())}


def inspect_email(value: str) -> dict[str, Any]:
    value = value.strip()
    match = re.fullmatch(r"([^\s@<>]+)@([^\s@<>]+\.[A-Za-z]{2,63})", value)
    if not match:
        return {"valid": False, "domain": None, "personal_provider": False}
    host = match.group(2).lower().rstrip(".")
    personal = host in {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "proton.me", "protonmail.com"}
    return {"valid": True, "domain": host, "personal_provider": personal}


def inspect_url(value: str) -> dict[str, Any]:
    from urllib.parse import urlsplit
    import ipaddress
    value = value.strip()
    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme.lower() not in {"http", "https"} or not host:
            return {"valid": False, "hostname": None, "scheme": parsed.scheme.lower(), "observations": []}
        observations = []
        if parsed.username is not None or parsed.password is not None:
            observations.append("URL contains embedded user information")
        if host.startswith("xn--") or ".xn--" in host:
            observations.append("URL contains a punycode hostname; review the displayed domain carefully")
        elif any(ord(char) > 127 for char in host):
            observations.append("URL contains an internationalized hostname; review its displayed form carefully")
        try:
            ipaddress.ip_address(host)
            observations.append("URL uses a raw IP address")
        except ValueError:
            pass
        if not value.lower().startswith("https://"):
            observations.append("URL does not use HTTPS")
        if host in {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd"}:
            observations.append("URL uses a known shortener")
        return {"valid": True, "hostname": host, "scheme": parsed.scheme.lower(), "observations": observations}
    except (ValueError, UnicodeError):
        return {"valid": False, "hostname": None, "scheme": None, "observations": []}


def tavily_search(company: str, timeout: float = 4.0) -> dict[str, Any]:
    """Optional real official-source discovery using Tavily's documented API."""
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not key:
        return {"status": "not_configured", "sources": []}
    payload = json.dumps({"api_key": key, "query": f"{company} official website careers", "search_depth": "basic", "max_results": 4,
                          "include_answer": False, "include_raw_content": False}).encode()
    req = Request("https://api.tavily.com/search", data=payload, headers={"Content-Type": "application/json", "User-Agent": "CareerShield-AI/2.0"}, method="POST")
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read(256_001)
        if len(raw) > 256_000:
            return {"status": "failed", "sources": []}
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("results", []), list):
            return {"status": "unavailable", "sources": []}
        sources = []
        for item in data.get("results", [])[:4]:
            if not isinstance(item, dict):
                continue
            url = item.get("url"); title = item.get("title")
            if not isinstance(url, str) or not isinstance(title, str):
                continue
            try:
                parsed = urlsplit(url)
                if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username is not None or parsed.password is not None:
                    continue
            except ValueError:
                continue
            try:
                relevance = float(item.get("score", 0))
                if not math.isfinite(relevance):
                    relevance = 0.0
            except (TypeError, ValueError):
                relevance = 0.0
            sources.append({"title": title[:240], "url": url[:2000], "provider": "Tavily", "retrieved_at": _now(),
                            "relevance": max(0.0, min(1.0, relevance)),
                            "excerpt": str(item.get("content", ""))[:600], "verification_status": "source_discovered_not_independently_verified"})
        return {"status": "completed" if sources else "completed_no_results", "sources": sources}
    except HTTPError as exc:
        return {"status": "rate_limited" if exc.code == 429 else "unavailable", "sources": []}
    except (TimeoutError, socket.timeout):
        return {"status": "timed_out", "sources": []}
    except URLError as exc:
        return {"status": "timed_out" if isinstance(exc.reason, (TimeoutError, socket.timeout)) else "unavailable", "sources": []}
    except (OSError, ValueError, TypeError, KeyError):
        return {"status": "unavailable", "sources": []}


class ToolRegistry:
    """Allowlisted tools with finite call budget, result size, and elapsed-time reporting."""
    def __init__(self, max_calls: int = 8, tool_timeout: float = 4.0, max_duration: float = 15.0):
        self.max_calls = max(1, min(int(max_calls), 8))
        self.tool_timeout = max(0.1, min(float(tool_timeout), 10.0))
        self.max_duration = max(1.0, min(float(max_duration), 30.0))
        self.started_at = time.monotonic()
        self.calls = 0

    def run(self, name: str, value: str) -> ToolResult:
        if self.calls >= self.max_calls:
            return ToolResult(name, "skipped", "Investigation tool-call budget reached.", {}, 0)
        if time.monotonic() - self.started_at >= self.max_duration:
            return ToolResult(name, "skipped", "Investigation duration budget reached.", {}, 0)
        funcs: dict[str, Callable[[str], dict[str, Any]]] = {
            "payment_language_detector": payment_language,
            "credential_request_detector": credential_language,
            "urgency_claim_detector": urgency_language,
            "role_completeness_checker": role_completeness,
            "email_domain_inspector": inspect_email,
            "url_structure_inspector": inspect_url,
        }
        if name == "official_source_search":
            func = lambda x: tavily_search(x, min(self.tool_timeout, max(0.1, self.max_duration - (time.monotonic() - self.started_at))))
        else:
            func = funcs.get(name)
        if func is None:
            return ToolResult(name, "skipped", "Tool is not registered.", {}, 0)
        self.calls += 1
        started = time.monotonic()
        try:
            data = func(value)
            status = data.pop("status", "completed")
            summary = (f"{len(data.get('matches', []))} matching passage(s)" if "matches" in data else
                       "Structured local inspection completed" if data else status.replace("_", " "))
            # Tool payloads are capped before they enter the report.
            safe = json.loads(json.dumps(data, ensure_ascii=False))
            return ToolResult(name, status, summary, safe, round((time.monotonic()-started)*1000), "Tavily" if name == "official_source_search" and status.startswith("completed") else "local")
        except Exception:
            return ToolResult(name, "failed", "Tool failed; no external claim was added.", {}, round((time.monotonic()-started)*1000))
