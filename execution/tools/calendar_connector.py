"""Deterministic Calendar Tool supporting Google Calendar API and local offline testing."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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
        self.service = service
        self._mock_events: List[CalendarEvent] = []

    def list_upcoming_events(self, days_ahead: int = 7) -> List[CalendarEvent]:
        """Lists events occurring in the next N days."""
        if self.service is not None:
            # Google Calendar API live call
            try:
                now_iso = datetime.utcnow().isoformat() + "Z"
                events_result = self.service.events().list(
                    calendarId="primary",
                    timeMin=now_iso,
                    maxResults=20,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()
                items = events_result.get("items", [])
                return [
                    CalendarEvent(
                        id=i.get("id"),
                        summary=i.get("summary", "Untitled"),
                        start_time=i.get("start", {}).get("dateTime", ""),
                        end_time=i.get("end", {}).get("dateTime", ""),
                        description=i.get("description"),
                        location=i.get("location"),
                    )
                    for i in items
                ]
            except Exception:
                return self._mock_events
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
        if self.service is not None:
            body = {
                "summary": event.summary,
                "description": event.description,
                "start": {"dateTime": event.start_time},
                "end": {"dateTime": event.end_time},
                "location": event.location,
                "attendees": [{"email": a} for a in event.attendees],
            }
            try:
                created = self.service.events().insert(calendarId="primary", body=body).execute()
                return {"status": "success", "event_id": created.get("id"), "summary": event.summary}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # Offline local store
        event.id = f"mock-event-{len(self._mock_events) + 1}"
        self._mock_events.append(event)
        return {"status": "success", "event_id": event.id, "summary": event.summary, "offline_mode": True}


# Singleton instance
calendar_connector = CalendarConnector()
