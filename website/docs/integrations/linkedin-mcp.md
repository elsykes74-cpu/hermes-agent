---
sidebar_position: 4
title: "LinkedIn MCP"
description: "Connect Hermes Agent to LinkedIn via LinkedIn's official MCP server — read your feed, draft posts, search people, and manage company pages, all from the agent"
---

# LinkedIn MCP

LinkedIn's official MCP server gives Hermes Agent direct access to your LinkedIn account. Once connected, you can ask Hermes to draft and schedule posts, search your network, pull engagement metrics, manage company pages, and pull context from LinkedIn into any workflow — all through natural conversation.

## Prerequisites

Before connecting, you need a LinkedIn Developer App that is approved for the scopes you want to use.

1. Go to [LinkedIn Developer Apps](https://www.linkedin.com/developers/apps) and create a new application.
2. Under **Products**, request **Share on LinkedIn** (for posting) and **Sign In with LinkedIn using OpenID Connect** (for profile access). Additional products such as **Marketing Developer Platform** unlock company page and analytics tools.
3. Under **Auth**, add `http://localhost` as an authorized redirect URL (Hermes uses a loopback callback to complete the OAuth flow).
4. Note your **Client ID** — LinkedIn will also generate a **Client Secret**, but Hermes uses Dynamic Client Registration when the server supports it, so the secret is usually handled automatically.

:::tip No app yet?
LinkedIn's [Develop with MCP](https://www.linkedin.com/developers/apps/develop-with-mcp) page walks through app creation and lists the exact scopes needed for the MCP server.
:::

## Connect in one command

```bash
hermes mcp add linkedin --preset linkedin
```

This saves the following to `~/.hermes/config.yaml` and immediately opens an OAuth browser flow:

```yaml
mcp_servers:
  linkedin:
    url: "https://api.linkedin.com/rest/mcp"
    auth: oauth
```

Hermes will print an authorization URL and attempt to open it in your browser. Approve the permissions on LinkedIn, and Hermes captures the callback automatically. Tokens are cached at `~/.hermes/mcp-tokens/linkedin.json` with restricted permissions — subsequent runs reuse them silently until they expire or you call `hermes mcp login linkedin`.

## Headless / remote setup

If Hermes runs on a server without a browser:

1. Hermes prints "Or paste the redirect URL here…" alongside the authorize URL.
2. Open the URL in your local browser, approve access.
3. Copy the full URL the browser ends up on (it will show a connection error — that is expected).
4. Paste the URL at the Hermes prompt.

Alternatively, set up an SSH port forward on the callback port before starting the flow:

```bash
ssh -N -L 8080:127.0.0.1:8080 user@your-server
```

See [OAuth over SSH](/guides/oauth-over-ssh) for the full walkthrough.

## Re-authenticate

If your tokens expire or you want to switch LinkedIn accounts:

```bash
hermes mcp login linkedin
```

This clears the cached tokens and triggers a fresh OAuth flow.

## Filter tools

LinkedIn's MCP server exposes a range of tools. Enable only what you need to keep the tool list small and reduce unnecessary permissions:

```yaml
mcp_servers:
  linkedin:
    url: "https://api.linkedin.com/rest/mcp"
    auth: oauth
    tools:
      include:
        - get_profile
        - create_post
        - search_people
```

Or exclude specific tools you want off-limits:

```yaml
mcp_servers:
  linkedin:
    url: "https://api.linkedin.com/rest/mcp"
    auth: oauth
    tools:
      exclude:
        - delete_post
```

Run `hermes mcp configure linkedin` at any time to interactively toggle tools with a checkbox UI.

## What you can do

Once connected, ask Hermes in plain English:

```text
Draft a LinkedIn post about our new open-source release. Keep it under 700 characters, professional tone.
```

```text
Search LinkedIn for ML engineers in San Francisco who have worked at AI startups.
```

```text
Pull my last 5 LinkedIn posts and summarize engagement — likes, comments, shares.
```

```text
What has my network been posting about this week? Give me the top themes.
```

```text
Update the bio on our company LinkedIn page to reflect the new product launch.
```

## Combining LinkedIn with other tools

LinkedIn data becomes more powerful when Hermes can combine it with other context. Some patterns that work well:

**Draft from notes:**
Keep a `linkedin-drafts.md` context file, and ask Hermes to turn bullet points into polished posts.

**Company page workflow:**
Pair LinkedIn with the GitHub MCP server — ask Hermes to write a LinkedIn announcement whenever a new release is tagged.

**Outreach research:**
Use LinkedIn search alongside web search to build a profile of a prospect before a call.

## Troubleshooting

**OAuth flow never opens a browser**

Hermes falls back to printing the URL when it cannot detect a browser. Copy and open it manually, approve, then paste the redirect URL back at the prompt.

**"insufficient permissions" error**

The tool you called requires a LinkedIn product your app has not been approved for. Check the [LinkedIn Developer Apps](https://www.linkedin.com/developers/apps) console under **Products** and request the relevant product.

**Tokens expire quickly**

LinkedIn access tokens have a 60-day TTL. Refresh tokens are longer-lived. Hermes handles refresh automatically; if refresh fails (token revoked, permissions changed), run `hermes mcp login linkedin`.

**Test the connection**

```bash
hermes mcp test linkedin
```

This probes the server and lists all discovered tools along with their descriptions.

## Related docs

- [MCP Integration](/user-guide/features/mcp) — Full MCP feature reference
- [Use MCP with Hermes](/guides/use-mcp-with-hermes) — Practical MCP patterns
- [OAuth over SSH](/guides/oauth-over-ssh) — Complete remote OAuth walkthrough
- [LinkedIn Developer Apps](https://www.linkedin.com/developers/apps) — Create and manage your LinkedIn app
