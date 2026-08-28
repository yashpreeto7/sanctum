"""Unit tests for Obsidian Vault and Calendar workspace endpoints."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from execution.tools.obsidian_connector import ObsidianConnector, ObsidianNote
from server.app import app


@pytest.fixture
def test_client():
    return TestClient(app)


def test_obsidian_connector_crud(tmp_path: Path):
    connector = ObsidianConnector(vault_path=tmp_path)

    # 1. Create a note
    note = ObsidianNote(
        title="Architecture Decision 01",
        content="We chose SQLite for local WAL-mode checkpointing.",
        tags=["architecture", "adr", "sqlite"],
        folder="Decisions",
    )
    res_create = connector.create_or_update_note(note)
    assert res_create["status"] == "success"
    assert res_create["title"] == "Architecture Decision 01"

    # 2. List all notes
    all_notes = connector.list_all_notes()
    assert len(all_notes) == 1
    assert all_notes[0]["title"] == "Architecture Decision 01"
    assert "sqlite" in all_notes[0]["tags"]
    assert all_notes[0]["folder"] == "Decisions"

    # 3. Read note
    read_data = connector.read_note("Decisions/Architecture Decision 01.md")
    assert read_data is not None
    assert "SQLite for local WAL-mode" in read_data["content"]

    # 4. Append daily log
    res_daily = connector.append_daily_log("Triaged 10 messages and deployed v2.4", section="AI Actions")
    assert res_daily["status"] == "success"
    daily_notes = [n for n in connector.list_all_notes() if n["is_daily"]]
    assert len(daily_notes) == 1

    # 5. Delete note
    deleted = connector.delete_note("Decisions/Architecture Decision 01.md")
    assert deleted is True
    assert len(connector.list_all_notes()) == 1  # Only daily note remains


def test_obsidian_api_endpoints(test_client):
    # 1. Status
    res_status = test_client.get("/api/obsidian/status")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["status"] == "connected"
    assert "vault_path" in status_data

    # 2. Create note via API
    res_create = test_client.post(
        "/api/obsidian/note",
        json={
            "title": "API Test Note",
            "content": "# Test Header\nNote content created via API.",
            "tags": ["unit-test", "fastapi"],
            "folder": "Tests",
        },
    )
    assert res_create.status_code == 200

    # 3. List notes
    res_list = test_client.get("/api/obsidian/notes")
    assert res_list.status_code == 200
    notes = res_list.json()["notes"]
    assert any(n["title"] == "API Test Note" for n in notes)

    # 4. Read note
    res_read = test_client.get("/api/obsidian/note?path=Tests/API Test Note.md")
    assert res_read.status_code == 200
    assert "Note content created via API" in res_read.json()["note"]["content"]

    # 5. Append Daily Log
    res_daily = test_client.post(
        "/api/obsidian/daily-log",
        json={"entry": "Automated unit test execution verified.", "section": "System Tests"},
    )
    assert res_daily.status_code == 200

    # 6. Delete Note
    res_del = test_client.delete("/api/obsidian/note?path=Tests/API Test Note.md")
    assert res_del.status_code == 200
