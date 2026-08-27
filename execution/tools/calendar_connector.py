"""Deterministic Calendar Tool supporting live Google Calendar API and local offline testing."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class CalendarEvent(BaseModel):
    """Structured calendar event representation."""

    id: Optional[str] = None
    summary: str
    description: Optional[str] = None
    start_time: str = Field(..., description="ISO format datetime string")
    end_time: str = Field(..., description="ISO format datetime string")
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)


class CalendarConnector:
    """Manages reading, scheduling, and conflict detection for calendar events."""

    def __init__(self, service: Optional[Any] = None):
        self._custom_service = service
        self._mock_events: List[CalendarEvent] = []

    def _get_service(self):
        if self._custom_service is not None:
            return self._custom_service

        token_path = Path(__file__).resolve().parent.parent.parent / ".tmp" / "google_token.json"
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path))
                return build("calendar", "v3", credentials=creds)
            except Exception:
                pass
        return None

    def list_upcoming_events(self, days_ahead: int = 7) -> List[CalendarEvent]:
        """Lists events occurring in the next N days."""
        service = self._get_service()
        if service is not None:
            try:
                now_iso = datetime.utcnow().isoformat() + "Z"
                events_result = service.events().list(
                    calendarId="primary",
                    timeMin=now_iso,
                    maxResults=20,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()
                items = events_result.get("items", [])
                live_events = []
                for i in items:
                    start = i.get("start", {}).get("dateTime") or i.get("start", {}).get("date")
                    end = i.get("end", {}).get("dateTime") or i.get("end", {}).get("date")
                    live_events.append(
                        CalendarEvent(
                            id=i.get("id"),
                            summary=i.get("summary", "Untitled"),
                            start_time=start or "",
                            end_time=end or "",
                            description=i.get("description"),
                            location=i.get("location"),
                        )
                    )
                if live_events:
                    return live_events
            except Exception:
                pass
        return self._mock_events

    def check_conflicts(self, start_time_iso: str, end_time_iso: str) -> List[CalendarEvent]:
        """Checks for overlapping events in the given time window."""
        conflicts = []
        try:
            req_start = datetime.fromisoformat(start_time_iso.replace("Z", "+00:00"))
            req_end = datetime.fromisoformat(end_time_iso.replace("Z", "+00:00"))

            for ev in self.list_upcoming_events():
                ev_start = datetime.fromisoformat(ev.start_time.replace("Z", "+00:00"))
                ev_end = datetime.fromisoformat(ev.end_time.replace("Z", "+00:00"))

                if max(req_start, ev_start) < min(req_end, ev_end):
                    conflicts.append(ev)
        except Exception:
            pass
        return conflicts

    def create_event(self, event: CalendarEvent) -> Dict[str, Any]:
        """Schedules a new calendar event."""
        service = self._get_service()
        if service is not None:
            body = {
                "summary": event.summary,
                "description": event.description,
                "start": {"dateTime": event.start_time},
                "end": {"dateTime": event.end_time},
                "location": event.location,
                "attendees": [{"email": a} for a in event.attendees],
            }
            try:
                created = service.events().insert(calendarId="primary", body=body).execute()
                return {"status": "success", "event_id": created.get("id"), "summary": event.summary, "provider": "google_calendar_api"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # Offline local store
        event.id = f"mock-event-{len(self._mock_events) + 1}"
        self._mock_events.append(event)
        return {"status": "success", "event_id": event.id, "summary": event.summary, "offline_mode": True}


# Singleton instance
calendar_connector = CalendarConnector()
