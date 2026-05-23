"""Apollo.io MCP server. People search + enrichment.
Apollo's free tier allows limited people enrichment; use for high-value records first.
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from lib.common import env, http_post

mcp = FastMCP("apollo")
BASE = "https://api.apollo.io/v1"


def _headers() -> dict[str, str]:
    return {"Cache-Control": "no-cache", "Content-Type": "application/json",
            "X-Api-Key": env("APOLLO_API_KEY")}


@mcp.tool()
def enrich_person(first_name: str, last_name: str, city: str = "", state: str = "", title_kw: str = "enrolled agent") -> dict:
    """Look up a person by name + location. Returns email, LinkedIn, title, firm if found."""
    body = {
        "first_name": first_name,
        "last_name": last_name,
        "reveal_personal_emails": False,
    }
    if city: body["organization_locations"] = [f"{city}, {state}".strip(", ")]
    data = http_post(f"{BASE}/people/match", json_body=body, headers=_headers())
    p = data.get("person") or {}
    if not p:
        return {"found": False}
    return {
        "found": True,
        "email": p.get("email"),
        "email_status": p.get("email_status"),
        "linkedin_url": p.get("linkedin_url"),
        "title": p.get("title"),
        "firm": (p.get("organization") or {}).get("name"),
        "firm_domain": (p.get("organization") or {}).get("primary_domain"),
        "city": p.get("city"),
        "state": p.get("state"),
    }


if __name__ == "__main__":
    mcp.run()
