"""Unit tests for Obsidian, Calendar, and Email connectors."""

import pytest
from execution.tools.calendar_connector import CalendarConnector, CalendarEvent
from execution.tools.gmail_connector import GmailConnector, OutboundEmail
from execution.tools.obsidian_connector import ObsidianConnector, ObsidianNote


def test_obsidian_note_and_daily_log(tmp_path):
    """Verify Obsidian connector creates notes and appends daily logs."""
    obsidian = ObsidianConnector(vault_path=tmp_path)

    # 1. Create note
    note = ObsidianNote(
        title="LangGraph Decision",
        content="Decided to use LangGraph with SQLite checkpoints.",
        tags=["architecture", "agent"],
    )
    result = obsidian.create_or_update_note(note)
    assert result["status"] == "success"
    assert (tmp_path / "LangGraph Decision.md").exists()

    # 2. Daily log append
    log_res = obsidian.append_daily_log(entry="Synced 4 emails successfully.")
    assert log_res["status"] == "success"
    assert (tmp_path / "Daily").exists()


def test_calendar_connector_conflict_and_scheduling():
    """Verify calendar connector schedules events and detects conflicts."""
    cal = CalendarConnector()

    event1 = CalendarEvent(
        summary="Architecture Review",
        start_time="2026-08-27T10:00:00Z",
        end_time="2026-08-27T11:00:00Z",
    )
    res = cal.create_event(event1)
    assert res["status"] == "success"

    # Overlapping conflict
    conflicts = cal.check_conflicts(
        start_time_iso="2026-08-27T10:30:00Z",
        end_time_iso="2026-08-27T11:30:00Z",
    )
    assert len(conflicts) == 1
    assert conflicts[0].summary == "Architecture Review"


def test_gmail_connector_draft_and_send():
    """Verify email connector drafting and sending."""
    gmail = GmailConnector()

    email = OutboundEmail(
        to="rahul@company.com",
        subject="DocDispatch Specs",
        body="Attached is the architecture blueprint.",
    )

    draft_res = gmail.create_draft(email)
    assert draft_res["status"] == "draft_created"

    send_res = gmail.send_email(email)
    assert send_res["status"] == "sent"
    assert len(gmail._sent_emails) == 1
