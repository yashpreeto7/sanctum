"""Unit tests for Calendar Connector, Deduplication, Past Schedule Retention, Festivals, and API endpoints."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from execution.tools.calendar_connector import CalendarConnector, CalendarEvent
from server.app import app


@pytest.fixture
def test_client():
    return TestClient(app)


def test_calendar_connector_crud_and_dedup(tmp_path: Path, monkeypatch):
    storage_file = tmp_path / "calendar_events.json"
    connector = CalendarConnector(storage_path=storage_file)
    monkeypatch.setattr(connector, "_get_service", lambda: None)

    # 1. Create an event in the past (e.g. 5 days ago)
    ev_past = CalendarEvent(
        summary="Retro Sprint Review",
        start_time="2026-08-20T10:00",
        end_time="2026-08-20T11:00",
        location="Room 101",
    )
    connector.create_event(ev_past)

    # 2. Create an event in the future
    ev1 = CalendarEvent(
        summary="Architecture Sync Meeting",
        start_time="2026-08-29T10:00",
        end_time="2026-08-29T11:00",
        location="Room 402",
        attendees=["alex@partner.org"],
        description="Discuss personal OS roadmap.",
    )
    res_create = connector.create_event(ev1)
    assert res_create["status"] == "success"
    assert res_create["summary"] == "Architecture Sync Meeting"

    # 3. List events without festivals (verifying past + future retention)
    events_schedule = connector.list_upcoming_events(days_back=30, days_ahead=30, include_festivals=False)
    assert len(events_schedule) == 2
    summaries = [e.summary for e in events_schedule]
    assert "Retro Sprint Review" in summaries
    assert "Architecture Sync Meeting" in summaries

    # 4. Attempt to create duplicate event (same summary and start_time)
    ev2 = CalendarEvent(
        summary="Architecture Sync Meeting",
        start_time="2026-08-29T10:00",
        end_time="2026-08-29T11:00",
        location="Room 402",
    )
    res_create2 = connector.create_event(ev2)
    assert res_create2["status"] == "success"

    # List events again - must NOT have duplicates!
    events_after = connector.list_upcoming_events(days_back=30, days_ahead=30, include_festivals=False)
    assert len(events_after) == 2

    # 5. Check conflict detection
    conflicts = connector.check_conflicts("2026-08-29T10:30:00", "2026-08-29T11:30:00")
    assert len(conflicts) == 1
    assert conflicts[0].summary == "Architecture Sync Meeting"

    # 6. Check festival listing
    festivals = connector.list_festivals(year=2026)
    assert len(festivals) > 0
    assert any("Diwali" in f.summary for f in festivals)
    assert any("Holi" in f.summary for f in festivals)

    # 7. Delete event
    deleted = connector.delete_event(ev1.id)
    assert deleted is True
    events_remaining = connector.list_upcoming_events(days_back=30, days_ahead=30, include_festivals=False)
    assert len(events_remaining) == 1
    assert events_remaining[0].summary == "Retro Sprint Review"


def test_calendar_api_endpoints(test_client):
    # 1. Create event via API
    res_create = test_client.post(
        "/api/calendar/create",
        json={
            "summary": "FastAPI Deployment Review",
            "start_time": "2026-08-30T14:00",
            "end_time": "2026-08-30T15:00",
            "location": "Google Meet",
            "attendees": ["jashan@example.com"],
            "description": "Verify uvicorn background workers.",
        },
    )
    assert res_create.status_code == 200
    data = res_create.json()
    assert data["status"] == "success"
    event_id = data["result"]["event_id"]

    # 2. List events via API
    res_list = test_client.get("/api/calendar/events?days_back=60&days_ahead=60&include_festivals=true")
    assert res_list.status_code == 200
    events = res_list.json()["events"]
    assert any("FastAPI Deployment Review" in e["summary"] for e in events)
    assert any(e.get("event_type") == "festival" for e in events)

    # 3. Test Festivals endpoint
    res_fest = test_client.get("/api/calendar/festivals?year=2026")
    assert res_fest.status_code == 200
    festivals = res_fest.json()["festivals"]
    assert len(festivals) > 0
    assert any("Independence Day" in f["summary"] for f in festivals)

    # 4. Delete event via API
    res_del = test_client.delete(f"/api/calendar/event?event_id={event_id}")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "success"
