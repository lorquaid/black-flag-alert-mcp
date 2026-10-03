# Black Flag Alert MCP Server

UK company credit-risk intelligence as native tools for your AI agent — Claude,
Cursor, Windsurf, Cline, ChatGPT connectors, Gemini, or any Model Context
Protocol client.

Black Flag Alert scores every company registered in England & Wales with the
R-Score (0–100) — filed accounts, filing behaviour, charges, CCJs and winding-up
activity combined into one number — and serves it through one MCP endpoint.

- Endpoint: https://blackflagalert.com/api/mcp (streamable HTTP, MCP 2025-06-18)
- API keys: free trial, no card — https://blackflagalert.com/developers
- Coverage: England & Wales (5.1M companies). SC/NI/R/FC/OE prefixes are out of coverage.
- Methodology: https://blackflagalert.com/methodology

## Tools

| Tool | What it does | Metering |
|---|---|---|
| `search_companies` | Find a company's 8-char number from its name (up to 20 matches) | free |
| `get_company` | Full profile: R-Score, financials, charges, CCJs, directors, narrative | calls |
| `get_risk_narrative` | Fast plain-English risk summary only (cheapest call) | calls |
| `get_contacts` | SMTP-verified emails, phone, domain | contact lookups |
| `batch_enrich` | Up to 50 companies in one call: score, status, overdue, exposure | calls |
| `usage` | Your key's rolling-24h usage vs limits | free |

## Connect (remote, no install)

Works with any client that supports remote MCP servers:

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

ChatGPT: Settings → Connectors → Create (paste the URL). Claude web: Settings →
Connectors → Add custom. Claude Code: `claude mcp add --transport http
black-flag-alert https://blackflagalert.com/api/mcp --header "Authorization:
Bearer <key>"`. Gemini: Settings → Apps → Connections.

## Install locally (stdio)

```bash
uv tool install bfa-mcp        # once published to PyPI
# or from source:
uv sync                        # in this repo
```

```json
{
  "mcpServers": {
    "black-flag-alert": {
      "command": "bfa-mcp",
      "env": { "BFA_API_KEY": "bfa_live_..." }
    }
  }
}
```

## Environment variables

| Variable | Required | Default |
|---|---|---|
| `BFA_API_KEY` | yes | — |
| `BFA_BASE_URL` | no | `https://blackflagalert.com` |

## Example

> **You:** "Should we extend £20k credit to Kimmeridge Projects?"
>
> **Agent:** `search_companies("Kimmeridge Projects")` → `04466987` →
> `get_company("04466987")` → "R-Score 93.87 (Very Low risk), no CCJs, no
> outstanding charges, net assets £254K. Suggested exposure: £24,000."

## License

MIT
