"""Unit tests for Gmail connector actions and FastAPI inbox endpoints."""

import pytest
from fastapi.testclient import TestClient
from execution.tools.gmail_connector import GmailConnector, InboundEmail
from server.app import app


@pytest.fixture
def test_client():
    return TestClient(app)


def test_gmail_connector_triage_actions():
    gmail = GmailConnector()
    test_email = InboundEmail(
        id="test-msg-123",
        thread_id="test-thread-123",
        sender="alex@partner.org",
        subject="Project Alpha Review",
        body="Let us sync on Alpha milestones.",
        received_at_timestamp=1700000000.0,
        is_read=False,
    )
    gmail._recent_cache = [test_email]

    # 1. Mark as read
    res_read = gmail.mark_as_read("test-msg-123")
    assert res_read["status"] == "success"
    assert test_email.is_read is True

    # 2. Mark as unread
    res_unread = gmail.mark_as_unread("test-msg-123")
    assert res_unread["status"] == "success"
    assert test_email.is_read is False

    # 3. Archive
    res_archive = gmail.archive_message("test-msg-123")
    assert res_archive["status"] == "success"
    assert "INBOX" in res_archive["removed"]

    # 4. Reply
    res_reply = gmail.send_reply(
        to="alex@partner.org",
        subject="Project Alpha Review",
        body="Sounds great, looking forward to it.",
        thread_id="test-thread-123",
    )
    assert res_reply["status"] == "sent"
    assert res_reply["subject"] == "Re: Project Alpha Review"

    # 5. Trash
    res_trash = gmail.trash_message("test-msg-123")
    assert res_trash["status"] == "success"
    assert "test-msg-123" not in [e.id for e in gmail._recent_cache]


def test_inbox_action_endpoint(test_client):
    """Test /api/inbox/action endpoint."""
    res = test_client.post(
        "/api/inbox/action",
        json={"id": "msg-endpoint-test-1", "action": "archive"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["action"] == "archive"


def test_inbox_draft_reply_endpoint(test_client):
    """Test /api/inbox/draft-reply endpoint."""
    res = test_client.post(
        "/api/inbox/draft-reply",
        json={
            "id": "msg-draft-1",
            "sender": "sarah@company.com",
            "subject": "Q3 Planning Sync",
            "body": "Can you send the quarterly budget spreadsheet?",
            "user_instructions": "Confirm I will email it by noon.",
            "tone": "concise",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["subject"] == "Re: Q3 Planning Sync"
    assert len(data["body"]) > 5


def test_inbox_send_reply_endpoint(test_client):
    """Test /api/inbox/send-reply endpoint."""
    res = test_client.post(
        "/api/inbox/send-reply",
        json={
            "to": "sarah@company.com",
            "subject": "Re: Q3 Planning Sync",
            "body": "Here is the confirmation.",
            "msg_id": "msg-draft-1",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"


def test_calendar_endpoints(test_client):
    """Test /api/calendar/events and /api/calendar/create endpoints."""
    create_res = test_client.post(
        "/api/calendar/create",
        json={
            "summary": "Sprint Retro",
            "start_time": "2026-08-28T16:00:00Z",
            "end_time": "2026-08-28T17:00:00Z",
            "description": "Bi-weekly sprint retrospective",
            "location": "Room 404",
        },
    )
    assert create_res.status_code == 200
    assert create_res.json()["status"] == "success"

    list_res = test_client.get("/api/calendar/events")
    assert list_res.status_code == 200
    events = list_res.json().get("events", [])
    assert any(e["summary"] == "Sprint Retro" for e in events)
