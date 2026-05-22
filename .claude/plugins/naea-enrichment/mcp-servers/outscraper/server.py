"""Outscraper MCP server. Three tools:
- find_business: Google Maps lookup for firm name + address → website domain
- find_linkedin: search LinkedIn profile by name + location + keyword
- find_emails: domain → emails associated with that domain
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from lib.common import env, http_get, normalize_domain

mcp = FastMCP("outscraper")
BASE = "https://api.app.outscraper.com"


def _headers() -> dict[str, str]:
    return {"X-API-KEY": env("OUTSCRAPER_API_KEY")}


@mcp.tool()
def find_business(name: str, city: str, state: str) -> dict:
    """Look up a tax firm on Google Maps. Returns name, website domain, phone, address."""
    q = f"{name} {city} {state}"
    data = http_get(f"{BASE}/maps/search-v2", params={"query": q, "limit": 1, "async": "false"}, headers=_headers())
    items = (data.get("data") or [[]])[0]
    if not items:
        return {"found": False}
    b = items[0]
    site = b.get("site") or ""
    return {
        "found": True,
        "name": b.get("name"),
        "domain": normalize_domain(site) if site else None,
        "website": site,
        "phone": b.get("phone"),
        "address": b.get("full_address"),
        "rating": b.get("rating"),
    }


@mcp.tool()
def find_linkedin(first_name: str, last_name: str, city: str, state: str, keyword: str = "enrolled agent tax") -> dict:
    """Find a LinkedIn profile URL using Google search via Outscraper."""
    q = f'site:linkedin.com/in "{first_name} {last_name}" "{city}" {keyword}'
    data = http_get(f"{BASE}/google-search-v2", params={"query": q, "limit": 5, "async": "false"}, headers=_headers())
    results = (data.get("data") or [[]])[0]
    for r in results:
        link = r.get("link", "")
        if "linkedin.com/in/" in link:
            return {"found": True, "url": link, "title": r.get("title"), "snippet": r.get("snippet")}
    return {"found": False}


@mcp.tool()
def find_emails(domain: str) -> dict:
    """Find emails associated with a domain (Outscraper Emails & Contacts Scraper)."""
    data = http_get(f"{BASE}/emails-and-contacts", params={"query": domain, "async": "false"}, headers=_headers())
    items = (data.get("data") or [])
    if not items:
        return {"found": False, "emails": []}
    row = items[0]
    return {
        "found": bool(row.get("emails")),
        "emails": row.get("emails", []),
        "phones": row.get("phones", []),
        "socials": row.get("socials", {}),
    }


if __name__ == "__main__":
    mcp.run()
