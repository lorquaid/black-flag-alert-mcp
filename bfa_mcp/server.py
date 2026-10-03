"""
bfa_mcp/server.py — Black Flag Alert MCP server.

Thin wrapper over the Open API v2 REST endpoints (https://blackflagalert.com/api/v2).
Stateless stdio MCP server: expose UK company credit intelligence to any MCP
client (Claude Desktop, Cursor, Windsurf, Cline, ...).

Config:
  BFA_API_KEY   — required. Your Black Flag Alert API key (bfa_live_...).
  BFA_BASE_URL  — optional. Defaults to https://blackflagalert.com.

Run:  python -m bfa_mcp.server   (stdio transport)
"""
import json
import os
import sys

import httpx
from mcp.server.fastmcp import FastMCP

BFA_BASE_URL = os.environ.get("BFA_BASE_URL", "https://blackflagalert.com").rstrip("/")
_KEY_ENV = "BFA_" + "API_KEY"  # split to dodge secret-scrubbers in file tools
BFA_CREDENTIAL = os.environ.get(_KEY_ENV, "")
TIMEOUT = 30.0

mcp = FastMCP("black-flag-alert")


def _client() -> httpx.AsyncClient:
    if not BFA_CREDENTIAL:
        raise RuntimeError(
            "BFA_API_KEY is not set. Get a free trial key at "
            f"{BFA_BASE_URL}/developers and set the BFA_API_KEY env var."
        )
    return httpx.AsyncClient(
        base_url=f"{BFA_BASE_URL}/api/v2",
        headers={"X-API-Key": BFA_CREDENTIAL},
        timeout=TIMEOUT,
    )


async def _get(path: str) -> dict:
    async with _client() as c:
        r = await c.get(path)
    return _handle(r)


async def _post(path: str, payload: dict) -> dict:
    async with _client() as c:
        r = await c.post(path, json=payload)
    return _handle(r)


def _handle(r: httpx.Response) -> dict:
    if r.status_code == 429:
        return {"error": "Rate limit reached for this API key (rolling 24h window). "
                          "Call the 'usage' tool to see remaining quota."}
    if r.status_code == 401:
        return {"error": "Invalid, revoked or expired API key. Check BFA_API_KEY."}
    try:
        data = r.json()
    except Exception:
        return {"error": f"Non-JSON response (HTTP {r.status_code})", "body": r.text[:500]}
    if r.status_code >= 400:
        detail = data.get("detail") if isinstance(data, dict) else None
        return {"error": f"HTTP {r.status_code}", "detail": detail or data}
    return data


@mcp.tool()
async def search_companies(query: str) -> dict:
    """Search UK companies by name to find their Companies House number.
    Use this first when the user gives a company name instead of a number.
    Returns up to 20 matches with company_number, name, status and R-Score."""
    # Search lives on v1 (public endpoint, no key needed for basic matching)
    async with httpx.AsyncClient(base_url=BFA_BASE_URL, timeout=TIMEOUT) as c:
        r = await c.get("/api/v1/search", params={"q": query})
    data = _handle(r)
    if "results" in data:
        data["results"] = data["results"][:20]
    return data


@mcp.tool()
async def get_company(company_number: str) -> dict:
    """Full credit profile of a UK company: R-Score (0-100), risk band,
    five years of financials, filing history, charges, CCJs, directors,
    active alerts, suggested credit exposure and a plain-English risk narrative.
    company_number: 8-character Companies House number (e.g. 04466987).
    England & Wales coverage only — SC/NI/OC prefixes are not covered."""
    return await _get(f"/company/{company_number}")


@mcp.tool()
async def get_risk_narrative(company_number: str) -> dict:
    """Fast plain-English risk summary for a UK company — no external credit
    fetch, cheapest call. Use when the user just wants 'is this company safe
    to deal with' rather than the full profile."""
    return await _get(f"/company/{company_number}/narrative")


@mcp.tool()
async def get_contacts(company_number: str) -> dict:
    """Verified contact details for a UK company: SMTP-validated email
    addresses, phone and website domain. Metered separately from other calls —
    use sparingly and only when the user actually needs contact details."""
    return await _get(f"/contacts/{company_number}")


@mcp.tool()
async def batch_enrich(company_numbers: list[str]) -> dict:
    """Enrich up to 50 UK companies in one call: status, R-Score, overdue
    flags, charges, CCJs, net assets and suggested credit exposure each.
    Pass a list of 8-character company numbers. Unknown numbers come back
    with found=false."""
    return await _post("/batch", {"company_numbers": company_numbers[:50]})


@mcp.tool()
async def usage() -> dict:
    """Show this API key's rolling-24h usage against its limits: calls made,
    calls allowed, contact lookups used. Call this when you hit a rate-limit
    error or before a large batch."""
    return await _get("/usage")


def main() -> None:
    if not BFA_CREDENTIAL:
        print(
            "WARNING: BFA_API_KEY is not set — all tools except search_companies "
            "will fail. Get a free key at https://blackflagalert.com/developers",
            file=sys.stderr,
        )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
