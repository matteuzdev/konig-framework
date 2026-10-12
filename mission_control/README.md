# KONIG Mission Control (local alpha)

Operator-facing dashboard for the **existing** KONIG framework. Does not replace ONIX, SOPs, Waves or engineering workflows.

## Run

```bash
# From repository root, after dependencies are installed
export KONIG_CONTROL_TOKEN="use-a-long-random-password"
# Optional integrations (never expose these to the browser):
export TELEGRAM_BOT_TOKEN="your-botfather-token"
export TELEGRAM_CHAT_ID="your-forum-or-chat-id"
export OPENAI_API_KEY="your-server-side-api-key"
uvicorn mission_control.server:app --host 127.0.0.1 --port 8765
```

On Windows PowerShell, use `$env:KONIG_CONTROL_TOKEN="..."`. Open http://127.0.0.1:8765 and enter the operator token. Keep the server loopback-only and do not expose it publicly; this is a local single-operator alpha, not a hardened public web app.

## Shipped

- Automatically discovers squad names, agent manifests and YAML workflows from `.agents/` and `squads/*`.
- Dedicated workspace for writing notes by squad, persisted to local SQLite (file path configurable with `KONIG_CONTROL_DB`).
- Authenticated server-side connection status for Telegram, including `getMe` health check; credentials never enter the browser.
- Read-only OpenAI key availability. It does not spend API credits.
- MCP/OAuth expansion panel explicitly marks unavailable functionality.
- Operator API requires a token; if none configured, it refuses access.

## Explicitly not yet implemented

- Real-time telemetry, event persistence, approvals, run/pause/abort workflow controls.
- User management, remote authentication, public hosting, multi-tenancy, production-grade auditing.
- Telegram inbound webhook, delivery/notification controls and forum topic mapping through the UI.
- OAuth authorization to third-party remote MCP services. This would require OIDC/OAuth discovery, PKCE, state, redirect callback, session management, encrypted storage, scopes, refresh and revocation, and tool permission approvals. OpenAI model inference is ordinarily configured separately with server-side API credentials. Do **not** offer a fake "Sign in with ChatGPT to use OpenAI API" flow.
- ONIX execution integration; dashboard never fakes active agents.

## Next integration contract

1. ONIX emits append-only `workflow.started`, `wave.started`, `agent.started`, `handoff.created`, `gate.failed`, `wave.completed`, `workflow.completed` events.
2. Store events persistently with immutable IDs, durable timestamps and run IDs, no prompts/secrets in the client feed.
3. Present an actual Wave graph with artifact and QA links.
4. Add server-side approve/reject/cancel actions with authorizations and audit log.
5. Wire Telegram notifications to approved events with chat/topic mapping.
6. Introduce remote MCP OAuth connector, only after securing sessions and tokens.

## Verification
`python -m pytest tests/test_mission_control.py` (tests supplied, not yet run by the author).
