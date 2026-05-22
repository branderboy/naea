"""NeverBounce MCP server. Single-email SMTP verification + pattern winner picker."""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from lib.common import env, http_get, email_patterns

mcp = FastMCP("neverbounce")
BASE = "https://api.neverbounce.com/v4"


@mcp.tool()
def verify(email: str) -> dict:
    """Verify a single email via NeverBounce. Returns result + flags."""
    data = http_get(
        f"{BASE}/single/check",
        params={"key": env("NEVERBOUNCE_API_KEY"), "email": email, "address_info": 1, "credits_info": 0},
    )
    return {
        "email": email,
        "result": data.get("result"),
        "is_valid": data.get("result") == "valid",
        "is_catchall": data.get("result") == "catchall",
        "flags": data.get("flags", []),
    }


@mcp.tool()
def pattern_winner(first_name: str, last_name: str, domain: str, max_checks: int = 4) -> dict:
    """Generate ranked email patterns and verify until one comes back valid.
    Stops early to save credits. Returns the winning email or None.
    """
    candidates = email_patterns(first_name, last_name, domain)[:max_checks]
    tried = []
    for cand in candidates:
        result = verify(cand)
        tried.append(result)
        if result["is_valid"]:
            return {"email": cand, "confidence": "pattern-guess", "attempts": tried}
        if result["is_catchall"]:
            return {"email": None, "confidence": "catch-all", "attempts": tried,
                    "note": "Domain accepts all addresses; pattern guess unreliable"}
    return {"email": None, "confidence": None, "attempts": tried}


if __name__ == "__main__":
    mcp.run()
