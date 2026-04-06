# MCP Servers I Actually Use (And How to Set Them Up)

*There are thousands of MCP servers. Most of them aren't worth your time. Here are the ones that actually changed how I work, the ones I tried and dropped, and why the hype doesn't match reality for most of them.*

---

MCP (Model Context Protocol) is everywhere in 2026. Every AI tool supports it. There are thousands of servers. YC president Garry Tan [said](https://x.com/garrytan/status/2031910564344262988) "MCP sucks honestly." Perplexity moved away from MCP internally, citing that tool schema overhead consumed up to 72% of the context window. And yet Pinterest is running 66,000 MCP invocations per month and saving 7,000 hours.

So which is it? Overhyped waste of time or genuinely useful?

After trying a bunch, my answer is: both. Most MCP servers aren't worth installing. But a few of them filled gaps that nothing else could.

## Quick Background

MCP is a protocol that lets AI tools (Claude Code, Cursor, Copilot, ChatGPT) connect to external services through a standardized interface. Anthropic created it in late 2024, donated it to the [Linux Foundation's Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) in December 2025. Now OpenAI, Google, Microsoft, and others are co-maintaining it.

An MCP server exposes **tools** (functions the AI calls), **resources** (data it reads), and **prompts** (templates for specific tasks). Two transport types: **stdio** for local servers, **HTTP** for remote ones.

97 million SDK downloads. Around 10,000 servers published. But according to [mcp.directory](https://mcp.directory) data, the top 10 servers by actual installs account for the vast majority of real usage. Most of the rest are weekend projects with near-zero users.

## The Rule That Saves You Money

Before installing any MCP server, ask: **does a CLI already exist for this?**

[ScaleKit ran a rigorous benchmark](https://www.scalekit.com/blog/mcp-vs-cli-use): GitHub MCP vs `gh` CLI. 75 runs, same tasks, Claude Sonnet 4.

| Task | CLI tokens | MCP tokens | Cost ratio |
|------|-----------|------------|------------|
| Get repo info | 1,365 | 44,026 | 32x |
| Check PR details | 1,648 | 32,279 | 20x |
| Analyze merged PRs | 5,010 | 33,712 | 7x |

**Reliability**: CLI 100% success. MCP 72% (failures were TCP timeouts to GitHub's server).

**Monthly at 10,000 operations**: ~$3 for CLI vs ~$55 for MCP.

Why the difference? GitHub's MCP server exposes 43 tool schemas. Every single call carries all 43 definitions in context, even when you only need one. The `gh` CLI? Claude already knows how to use it from training data. No schema bloat.

**My rule: if a mature CLI exists, use the CLI.** This covers `gh`, `git`, `docker`, `kubectl`, `aws`, `gcloud`, `psql`. The model knows these tools. MCP adds cost without adding capability.

MCP fills the gap for services that don't have CLIs the model can use: Notion, Sentry, Figma, Slack, Linear.

## The Servers I Keep Installed

### Context7: Fresh Documentation

The most installed MCP server by a wide margin ([50,000+ GitHub stars, 600,000+ weekly npm downloads](https://github.com/upstash/context7)). Solves a real problem: AI models generate code using outdated API syntax because their training data is months old.

Context7 fetches current, version-specific documentation at query time. When Claude needs to use a library, it pulls the actual current docs instead of guessing from stale training data.

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

No API key needed. The `@latest` tag is fine for personal dev, pin a specific version for anything shared or production. The free tier gives you about 1,000 requests/month (reduced from 6,000 in January 2026).

**The catch**: In early 2026, [Noma Security discovered](https://www.noma.security/blog/contextcrush) that Context7's "Custom Rules" feature could be exploited. Anyone with a GitHub account could register a library and inject malicious instructions that would be served to every developer querying that library. The attack chain: register fake library, inject instructions to read `.env` files, exfiltrate contents. It was patched within 5 days, but it's a reminder that even the most popular MCP server can be a vector.

Competition is growing: Deepcon and Docfork offer similar functionality.

### Sentry: Production Error Context

When debugging production issues, copying error details from Sentry into Claude is tedious. With the Sentry MCP, I paste an error link and Claude reads the full stack trace, error context, and affected users directly.

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

Authenticates through the browser on first use. After that, Claude searches errors, reads stack traces, and suggests fixes with full production context.

### Notion: Reading Specs

I keep project specs and technical decisions in Notion. The Notion MCP lets Claude search my workspace and read specific pages.

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

Real use case: "Read the API design spec in Notion and implement the endpoints." Claude reads the spec instead of me copying it.

Gets slow on large workspaces because of Notion API rate limits. For targeted reads it works.

### Playwright: Browser Automation

For frontend work, Playwright MCP lets Claude control a browser. Screenshots, form filling, clicking, end-to-end test verification.

```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

I use it for visual verification. "Implement this change, open the page, take a screenshot, compare with the design." Gives Claude "eyes" for frontend work.

Note: the Puppeteer MCP server is deprecated. Use Playwright.

### PostgreSQL: Safe Database Access

Read-only database access for investigating production data.

```bash
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres \
  "postgresql://user:pass@host/db"
```

For debugging queries, checking data states, understanding schema relationships. **Read-only.** I don't give write access to production databases through MCP.

## What I Tried and Dropped

**GitHub MCP.** The `gh` CLI does the same thing for 10-32x fewer tokens and 100% reliability. No point paying the overhead.

**Filesystem MCP.** Claude Code already has built-in file operations. Redundant.

**Memory MCP.** Claude Code's auto memory works better and requires no setup.

**Sequential Thinking.** Adds latency to every interaction. For architecture decisions, Plan Mode does the same thing without the overhead.

## Setting Up .mcp.json

MCP servers are configured in JSON. Two scopes:

**Personal** (all your projects): `~/.claude/.mcp.json`
**Project** (shared with team): `.mcp.json` in project root

Example project config:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "sentry": {
      "type": "http",
      "url": "https://mcp.sentry.dev/mcp"
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

Environment variables use `${VAR}` or `${VAR:-default}` syntax. If a required variable is missing with no default, Claude Code won't start that server.

### Gotchas that will waste your time

**Flag ordering.** All flags (`--transport`, `--env`, `--scope`) must come before the server name in `claude mcp add`. Get the order wrong and the command silently fails.

**Windows npx.** On Windows (not WSL), npx-based servers need a `cmd /c` wrapper or you get "Connection closed" errors.

**SSE is deprecated.** Use `--transport http` for all remote servers.

**Token limits.** Claude Code warns at 10,000 tokens of MCP output. Override with `MAX_MCP_OUTPUT_TOKENS=50000` if a server returns large payloads.

**Project servers need approval.** When you open a project with a `.mcp.json`, Claude Code asks before connecting to those servers. Reset with `claude mcp reset-project-choices`.

**Startup timeout.** Some servers are slow to start. Configure with `MCP_TIMEOUT=10000 claude` (10 seconds).

## Building Your Own

If you need to connect Claude to an internal system, building a custom MCP server is simpler than you'd expect. [FastMCP](https://gofastmcp.com) (Python) powers roughly 70% of MCP servers across all languages:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("internal-api")

@mcp.tool()
async def search_tickets(query: str) -> str:
    """Search internal ticket system.

    Args:
        query: The search query
    """
    results = await internal_api.search(query)
    return format_results(results)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Tool definitions are generated from type hints and docstrings. No schema writing.

Test with `mcp dev server.py` (opens the MCP Inspector at `http://127.0.0.1:6274`).

Two rules:
1. **Never print to stdout** in stdio servers. It corrupts JSON-RPC messages. Use `print("...", file=sys.stderr)`.
2. **Use async for I/O.** A synchronous function blocks the entire MCP server.

[Pinterest's experience](https://medium.com/pinterest-engineering/building-an-mcp-ecosystem-at-pinterest-d881eb4c16f1) is the strongest case for custom servers: their Presto MCP (data warehouse queries) is their highest-traffic server, and the team estimates 7,000 hours saved per month. But they also found early on that "spinning up a new MCP server required too much work" until they built a unified deployment pipeline.

For learning, [Microsoft's MCP for Beginners](https://github.com/microsoft/mcp-for-beginners) has examples in 6 languages.

## Security: Take It Seriously

This section exists because the numbers are bad.

Between January and February 2026, [30+ CVEs were filed](https://www.practical-devsecops.com/mcp-security-vulnerabilities/) against MCP servers, clients, and infrastructure. The worst: [CVE-2025-6514](https://nvd.nist.gov/vuln/detail/CVE-2025-6514) in `mcp-remote`, an OS command injection with CVSS 9.6 that affected 437,000+ downloads.

[AgentSeal scanned 1,808 MCP servers](https://agentseal.org/blog/mcp-server-security-findings): 66% had security findings. A broader [Endor Labs analysis](https://www.endorlabs.com/learn/the-state-of-mcp-security) of 2,614 implementations found 82% vulnerable to path traversal, 67% with code injection risk.

A malicious package impersonating the Postmark email service was uploaded to the MCP registry, exfiltrating API keys because the registry lacked vetting.

What I do:

**Vendor-maintained servers only.** I don't install random community MCP servers. If it's not from the service provider (Sentry, Notion, Microsoft) or widely trusted with clear maintainers, I skip it.

**Read-only by default.** My PostgreSQL server is read-only. If a server offers write operations I don't need, I don't use them.

**Pin versions in production.** Don't use `@latest` for anything beyond personal dev. Pin to a specific version and update deliberately.

**Run `uvx mcp-scan`** on your configuration periodically. It scans your installed servers for known vulnerabilities in under 30 seconds.

The [Claude Code docs](https://code.claude.com/docs/en/mcp) say it plainly: "Use third party MCP servers at your own risk."

## Where MCP Actually Shines

Individual developers automating their own workflow? Honestly, CLIs cover most of it. MCP's real value shows up in organizations.

[Pinterest's deployment](https://medium.com/pinterest-engineering/building-an-mcp-ecosystem-at-pinterest-d881eb4c16f1) is the best example: cloud-hosted servers with centralized auth (end-user JWT via Envoy, business-group-based access gating), tool-level authorization decorators, and mandatory security review for every non-experimental server. 844 monthly active users, many of them non-engineers accessing data warehouses through agents.

[Charles Chen](https://chrlschn.dev/blog/2026/03/mcp-is-dead-long-live-mcp/) makes the point that critics are right about MCP for individual use but wrong for organizations. MCP over local stdio adds little over custom CLIs. But MCP over remote HTTP with centralized servers solves auth revocation (engineer leaves = revoke token), telemetry (OpenTelemetry built-in), and org-wide delivery of updated tools and documentation.

For a solo developer? Start with Context7 and add others only when you hit a real gap. For a team? MCP is worth the investment if you have internal systems that need AI access with proper auth and audit trails.

---

## Further Reading

**Official:**
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Claude Code MCP Documentation](https://code.claude.com/docs/en/mcp)
- [Build an MCP Server Tutorial](https://modelcontextprotocol.io/docs/develop/build-server)
- [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)

**Real-World:**
- [Pinterest: Building an MCP Ecosystem](https://medium.com/pinterest-engineering/building-an-mcp-ecosystem-at-pinterest-d881eb4c16f1)
- [Pragmatic Engineer: Building MCP Servers in the Real World](https://newsletter.pragmaticengineer.com/p/mcp-deepdive)
- [ScaleKit: MCP vs CLI Benchmark](https://www.scalekit.com/blog/mcp-vs-cli-use)

**Security:**
- [AgentSeal: MCP Server Security Findings](https://agentseal.org/blog/mcp-server-security-findings)
- [Noma Security: ContextCrush Vulnerability](https://www.noma.security/blog/contextcrush)
- [30 CVEs in 60 Days](https://www.practical-devsecops.com/mcp-security-vulnerabilities/)

**Learning:**
- [Microsoft: MCP for Beginners](https://github.com/microsoft/mcp-for-beginners)
- [FastMCP Documentation](https://gofastmcp.com)

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience building distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*
