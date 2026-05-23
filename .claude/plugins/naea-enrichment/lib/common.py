"""Shared helpers for MCP servers in this plugin."""
from __future__ import annotations

import os
import re
import json
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


def env(key: str, required: bool = True) -> str:
    val = os.environ.get(key, "")
    if required and not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=16))
def http_get(url: str, params: dict | None = None, headers: dict | None = None, timeout: float = 30.0) -> dict[str, Any]:
    r = httpx.get(url, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=16))
def http_post(url: str, json_body: dict | None = None, headers: dict | None = None, timeout: float = 30.0) -> dict[str, Any]:
    r = httpx.post(url, json=json_body, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def email_patterns(first: str, last: str, domain: str) -> list[str]:
    """Generate ranked email candidates from name + domain."""
    f = re.sub(r"[^a-z]", "", first.lower())
    l = re.sub(r"[^a-z]", "", last.lower())
    if not f or not l or not domain:
        return []
    return [
        f"{f}.{l}@{domain}",
        f"{f}{l}@{domain}",
        f"{f[0]}{l}@{domain}",
        f"{f}@{domain}",
        f"{l}@{domain}",
        f"{f}_{l}@{domain}",
        f"{f}.{l[0]}@{domain}",
        f"{f[0]}.{l}@{domain}",
    ]


def normalize_domain(url_or_domain: str) -> str:
    s = url_or_domain.lower().strip()
    s = re.sub(r"^https?://", "", s)
    s = re.sub(r"^www\.", "", s)
    s = s.split("/", 1)[0]
    return s
