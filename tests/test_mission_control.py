"""Mission Control API smoke tests; uses isolated temp database and no network."""
from fastapi.testclient import TestClient
from mission_control import server


def test_auth_required(monkeypatch):
    monkeypatch.setenv("KONIG_CONTROL_TOKEN", "local-test-secret")
    client = TestClient(server.app)
    assert client.get("/api/overview").status_code == 401
    assert client.get("/api/overview", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_squad_inventory(monkeypatch):
    monkeypatch.setenv("KONIG_CONTROL_TOKEN", "local-test-secret")
    client = TestClient(server.app)
    response = client.get("/api/overview", headers={"Authorization": "Bearer local-test-secret"})
    assert response.status_code == 200
    squads = response.json()["squads"]
    assert any(s["id"] == ".agents" for s in squads)
    assert all(s["activity"] == "not_connected" for s in squads)


def test_notes_persist(monkeypatch, tmp_path):
    monkeypatch.setenv("KONIG_CONTROL_TOKEN", "local-test-secret")
    monkeypatch.setattr(server, "DB", tmp_path / "local.db")
    client = TestClient(server.app)
    auth = {"Authorization": "Bearer local-test-secret"}
    created = client.post("/api/notes", headers=auth, json={"squad": ".agents", "body": "Test note"})
    assert created.status_code == 200
    notes = client.get("/api/notes", headers=auth).json()
    assert notes[0]["body"] == "Test note"
    assert notes[0]["squad"] == ".agents"


def test_telegram_no_credentials(monkeypatch):
    monkeypatch.setenv("KONIG_CONTROL_TOKEN", "local-test-secret")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    client = TestClient(server.app)
    result = client.get("/api/telegram/check", headers={"Authorization": "Bearer local-test-secret"}).json()
    assert result["connected"] is False
