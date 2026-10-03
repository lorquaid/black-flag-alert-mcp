# Black Flag Alert MCP Server

UK company credit intelligence as native tools for your AI agent — Claude Desktop,
Cursor, Windsurf, Cline, or any Model Context Protocol client.

The R-Score (0–100) combines filed accounts, filing behaviour, charges, CCJs
and winding-up activity into one credit-risk number for UK companies.
This server wraps the Black Flag Alert Open API v2 so your agent can query it directly.

## Tools exposed

| Tool | What it does | Metering |
|---|---|---|
| `search_companies` | Find a company's 8-char number from its name (up to 20 matches) | free (v1) |
| `get_company` | Full profile: R-Score, financials, charges, CCJs, directors, narrative | calls |
| `get_risk_narrative` | Fast plain-English risk summary only (cheapest call) | calls |
| `get_contacts` | SMTP-verified emails, phone, domain | contact lookups |
| `batch_enrich` | Up to 50 companies in one call: score, status, overdue, exposure | calls |
| `usage` | Your key's rolling-24h usage vs limits | free |

## 1. Get an API key

Free trial — no card, 14 days, 100 calls + 20 contact lookups per day:

- Sign up at https://blackflagalert.com/developers (key shown instantly), or
- `POST https://blackflagalert.com/api/v2/signup` with `{"email": "you@company.com"}`

## 2. Connect — hosted endpoint (no install)

The server is hosted at `https://blackflagalert.com/api/mcp` (streamable HTTP).
No clone, no local process — just point your MCP client at the URL:

```json
{
  "mcpServers": {
    "black-flag-alert": {
      "type": "http",
      "url": "https://blackflagalert.com/api/mcp",
      "headers": {
        "Authorization": "Bearer bfa_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

Works with any client that supports remote MCP servers (Cursor, Claude Desktop
with remote-HTTP support, Claude Code `--mcp-config`, Cline, ...). Same key,
same quota and usage accounting as the REST API.

## 2b. Or install the local stdio server

Option A — run from this directory with `uv`:

```bash
cd /path/to/bfa-mcp
uv sync          # installs mcp + httpx
```

Option B — pip:

```bash
python -m venv .venv && .venv/bin/pip install .
```

## 3. Configure your MCP client

### Claude Desktop / Cursor / Windsurf (uvx, recommended)

Add to your MCP config (`claude_desktop_config.json` or `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "black-flag-alert": {
      "command": "uvx",
      "args": ["--from", "/path/to/bfa-mcp", "bfa-mcp"],
      "env": {
        "BFA_API_KEY": "bfa_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Direct Python (no uvx)

```json
{
  "mcpServers": {
    "black-flag-alert": {
      "command": "/path/to/bfa-mcp/.venv/bin/python",
      "args": ["-m", "bfa_mcp"],
      "env": {
        "BFA_API_KEY": "bfa_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "BFA_BASE_URL": "https://blackflagalert.com"
      }
    }
  }
}
```

## Environment variables

| Variable | Required | Default |
|---|---|---|
| `BFA_API_KEY` | yes | — (tools except search will fail without it) |
| `BFA_BASE_URL` | no | `https://blackflagalert.com` |

## Example conversation

> **You:** "Should we extend credit to Kimmeridge Projects? Check their risk."
>
> **Agent:** calls `search_companies("Kimmeridge Projects")` → finds `04466987`,
> then `get_company("04466987")` → "R-Score 94/100 (band A, low risk), no CCJs,
> no outstanding charges, net assets £254.5K. Suggested credit exposure: £24,000."

## Coverage & limits

- England & Wales companies only. Scottish (`SC`/`SLP`), Northern Irish
  (`NI`/`R`) and overseas (`FC`/`OE`) numbers return `coverage:
  "out_of_coverage"` with a reason — a coverage boundary, not an error.
- Trial: 100 calls + 20 contact lookups per rolling 24h. Check with the `usage`
  tool. Email support@blackflagalert.com for production limits.

## Troubleshooting

- **"BFA_API_KEY is not set"** — add the env var to your MCP client config.
- **429 errors** — rolling-24h limit reached; the agent should call `usage`
  and back off.
- **401 errors** — key revoked/expired; issue a new one at /developers.

---
Black Flag Alert · https://blackflagalert.com · support@blackflagalert.com
