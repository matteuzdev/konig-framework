"""KONIG Mission Control MVP — local operator workspace. No workflow execution by default.

Start with: KONIG_CONTROL_TOKEN=<long-random-secret> uvicorn mission_control.server:app --host 127.0.0.1 --port 8765
Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the server environment, never in the browser.
"""
from __future__ import annotations
import json
import os
import sqlite3
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
DB = Path(os.environ.get("KONIG_CONTROL_DB", str(ROOT / "scratch" / "mission-control.db")))
app = FastAPI(title="KONIG Mission Control", version="0.1.0")


def authorize(authorization: str | None) -> None:
    import hmac
    expected = os.environ.get("KONIG_CONTROL_TOKEN", "")
    if not expected:
        raise HTTPException(503, "Set KONIG_CONTROL_TOKEN to enable the operator API")
    supplied = authorization[7:] if authorization and authorization.startswith("Bearer ") else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(401, "Operator authentication required")


def database():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, squad TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL)")
    con.commit()
    return con


def discover_squads():
    squads = []
    for directory in [ROOT / ".agents", *(ROOT / "squads").glob("*")]:
        if not directory.is_dir():
            continue
        agents_dir = directory / "agents"
        workflows_dir = directory / "workflows"
        squads.append({
            "id": ".agents" if directory.name == ".agents" else directory.name,
            "name": "Engineering" if directory.name == ".agents" else directory.name.title(),
            "agents": sorted(p.stem for p in agents_dir.glob("*.md")) if agents_dir.is_dir() else [],
            "workflows": sorted(p.stem for p in workflows_dir.glob("*.yaml")) if workflows_dir.is_dir() else [],
            "activity": "not_connected",
        })
    return squads


@app.get("/", response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / "index.html").read_text(encoding="utf-8")


@app.get("/api/overview")
def overview(authorization: str | None = Header(default=None)):
    authorize(authorization)
    return {
        "mode": "read_only",
        "squads": discover_squads(),
        "telegram": {"configured": bool(os.getenv("TELEGRAM_BOT_TOKEN")), "chat_configured": bool(os.getenv("TELEGRAM_CHAT_ID"))},
        "openai": {"api_key_configured": bool(os.getenv("OPENAI_API_KEY")), "oauth": "not_implemented"},
        "mcp": {"status": "planned", "servers": []},
        "note": "No live agent execution telemetry is wired yet. These are actual filesystem manifests, not running agent counts."
    }


class NoteIn(BaseModel):
    squad: str = Field(min_length=1, max_length=60)
    body: str = Field(min_length=1, max_length=4000)


@app.get("/api/notes")
def get_notes(authorization: str | None = Header(default=None)):
    authorize(authorization)
    with database() as con:
        rows = con.execute("SELECT id, squad, body, created FROM notes ORDER BY id DESC LIMIT 100").fetchall()
    return [dict(zip(["id", "squad", "body", "created"], r)) for r in rows]


@app.post("/api/notes")
def add_note(note: NoteIn, authorization: str | None = Header(default=None)):
    authorize(authorization)
    valid = {s["id"] for s in discover_squads()}
    if note.squad not in valid:
        raise HTTPException(422, "Unknown squad")
    with database() as con:
        cur = con.execute("INSERT INTO notes(squad, body, created) VALUES(?,?,?)",
                          (note.squad, note.body, datetime.now(timezone.utc).isoformat()))
        return {"id": cur.lastrowid, "saved": True}


@app.get("/api/telegram/check")
def check_telegram(authorization: str | None = Header(default=None)):
    authorize(authorization)
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return {"connected": False, "reason": "TELEGRAM_BOT_TOKEN missing"}
    try:
        # Bot API token is only ever used server-side. Never return URL, headers, or token.
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getMe", timeout=5) as response:
            result = json.loads(response.read(8192))
        user = result.get("result", {})
        return {"connected": bool(result.get("ok")), "bot_username": user.get("username") if result.get("ok") else None}
    except Exception:
        return {"connected": False, "reason": "Bot API validation failed; check credentials/network"}


@app.get("/api/integrations")
def integrations(authorization: str | None = Header(default=None)):
    authorize(authorization)
    return {
        "telegram": {"mode": "environment", "token_present": bool(os.getenv("TELEGRAM_BOT_TOKEN")), "chat_present": bool(os.getenv("TELEGRAM_CHAT_ID"))},
        "openai": {"mode": "server_side_api_key", "configured": bool(os.getenv("OPENAI_API_KEY"))},
        "mcp": {"remote_oauth": "not_implemented", "requires": ["OIDC/OAuth discovery", "PKCE", "state", "server-side encrypted token store", "scopes", "refresh and revocation", "tool allowlist", "human approvals"]},
    }
