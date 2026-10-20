# König Reach — experimental web intelligence adapter

First-party experimental component. No upstream source has been copied.

## Run
Python >=3.10 and dependencies: httpx, beautifulsoup4.

```bash
pip install -e '.[test]'
konig-reach 'https://example.com' --allow-host example.com
pytest -q
```

Security: explicit allowlist; checks globally routable DNS answers; redirects disabled; 2 MB response cap; 30s max timeout; ambient proxies disabled; public HTML only. **Not production-safe against DNS TOCTOU/rebinding between resolution and connect**: enforce an egress firewall/filtered proxy; honor target robots/terms, privacy and crawl rate policies before operation. No credentials, stealth, WAF bypass or scraping of gated/private sites.

Local evaluation on 2026-10-20: 12/12 offline pytest cases passed. 10 Red Team families covered with **simulated fixtures**; no external penetration test, browser extraction, Agent-Reach or Scrapling integration, benchmark or production audit.

ARC evidence/protocol: https://github.com/matteuzdev/hianto-intelligence-system/blob/main/20-forja/COLISEUM-PROTOCOL.md.
Integration direction: vetted Scrapling as optional web backend; Agent-Reach CLI/API connectors under explicit access authority; browser adapter only after legal and security verification. 
