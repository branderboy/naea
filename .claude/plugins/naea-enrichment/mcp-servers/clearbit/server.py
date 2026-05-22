"""Clearbit MCP server. Optional last-resort enrichment (most expensive)."""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
from mcp.server.fastmcp import FastMCP
from lib.common import env

mcp = FastMCP("clearbit")
BASE = "https://person-stream.clearbit.com/v2/people/find"


@mcp.tool()
def find_by_email(email: str) -> dict:
    """Enrich a known email with Clearbit person data (LinkedIn, title, employer)."""
    r = httpx.get(BASE, params={"email": email},
                  auth=(env("CLEARBIT_API_KEY"), ""), timeout=30)
    if r.status_code == 404:
        return {"found": False}
    r.raise_for_status()
    d = r.json()
    return {
        "found": True,
        "linkedin_url": (d.get("linkedin") or {}).get("handle"),
        "title": (d.get("employment") or {}).get("title"),
        "firm": (d.get("employment") or {}).get("name"),
        "firm_domain": (d.get("employment") or {}).get("domain"),
    }


if __name__ == "__main__":
    mcp.run()
