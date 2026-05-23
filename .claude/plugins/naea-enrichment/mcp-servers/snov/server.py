"""Snov.io MCP server. Optional fallback. Uses domain search + email finder."""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
from mcp.server.fastmcp import FastMCP
from lib.common import env

mcp = FastMCP("snov")
BASE = "https://api.snov.io"
_token: dict[str, str] = {}


def _get_token() -> str:
    if _token.get("v"):
        return _token["v"]
    r = httpx.post(f"{BASE}/v1/oauth/access_token", data={
        "grant_type": "client_credentials",
        "client_id": env("SNOV_CLIENT_ID"),
        "client_secret": env("SNOV_CLIENT_SECRET"),
    }, timeout=30)
    r.raise_for_status()
    _token["v"] = r.json()["access_token"]
    return _token["v"]


@mcp.tool()
def find_email_by_name(first_name: str, last_name: str, domain: str) -> dict:
    """Snov 'Email Finder' — guesses + verifies the email for a name at a domain."""
    r = httpx.post(f"{BASE}/v1/get-emails-from-names",
                   data={"access_token": _get_token(), "firstName": first_name,
                         "lastName": last_name, "domain": domain}, timeout=30)
    r.raise_for_status()
    data = r.json()
    emails = data.get("data", {}).get("emails", []) if isinstance(data.get("data"), dict) else []
    if not emails:
        return {"found": False}
    best = emails[0]
    return {"found": True, "email": best.get("email"), "status": best.get("emailStatus")}


if __name__ == "__main__":
    mcp.run()
