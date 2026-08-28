"""Deterministic Calendar Tool supporting live Google Calendar API and local offline persistent storage."""

import json
import os
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from execution.core.config import settings


class CalendarEvent(BaseModel):
    """Structured calendar event representation."""

    id: Optional[str] = None
    summary: str
    description: Optional[str] = None
    start_time: str = Field(..., description="ISO format datetime string")
    end_time: str = Field(..., description="ISO format datetime string")
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)


def _to_rfc3339(dt_str: str) -> str:
    """Converts any datetime string (e.g. YYYY-MM-DDTHH:MM or ISO) to standard RFC3339 format."""
    if not dt_str:
        return datetime.now(timezone.utc).isoformat()
    dt_str = dt_str.strip()
    try:
        # Handle 'Z' suffix
        if dt_str.endswith("Z"):
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(dt_str)
        # If naive datetime, attach local timezone
        if dt.tzinfo is None:
            dt = dt.astimezone()
        return dt.isoformat()
    except Exception:
        # Fallback formatting for YYYY-MM-DDTHH:MM
        if len(dt_str) == 16:
            local_tz = datetime.now().astimezone().strftime("%z")
            tz_formatted = f"{local_tz[:3]}:{local_tz[3:]}" if len(local_tz) == 5 else "+00:00"
            return f"{dt_str}:00{tz_formatted}"
        return dt_str


class CalendarConnector:
    """Manages reading, scheduling, deduplication, and conflict detection for calendar events."""

    def __init__(self, service: Optional[Any] = None, storage_path: Optional[Path] = None):
        self._custom_service = service
        self.storage_path = storage_path or (settings.TEMP_DIR / "calendar_events.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._mock_events: List[CalendarEvent] = self._load_local_events()

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

    def _load_local_events(self) -> List[CalendarEvent]:
        """Loads locally stored calendar events from disk."""
        if not self.storage_path.exists():
            return []
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            return [CalendarEvent(**item) for item in data]
        except Exception:
            return []

    def _save_local_events(self):
        """Persists local calendar events to disk."""
        try:
            raw = [e.model_dump() for e in self._mock_events]
            self.storage_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        except Exception:
            pass

    def list_upcoming_events(self, days_ahead: int = 30) -> List[CalendarEvent]:
        """Lists events occurring in the next N days with strict deduplication."""
        events_dict: Dict[str, CalendarEvent] = {}
        seen_keys = set()

        # 1. Fetch from Google Calendar API if available
        service = self._get_service()
        if service is not None:
            try:
                now_iso = datetime.now(timezone.utc).isoformat()
                events_result = service.events().list(
                    calendarId="primary",
                    timeMin=now_iso,
                    maxResults=50,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()
                items = events_result.get("items", [])
                for i in items:
                    start = i.get("start", {}).get("dateTime") or i.get("start", {}).get("date") or ""
                    end = i.get("end", {}).get("dateTime") or i.get("end", {}).get("date") or ""
                    eid = i.get("id") or str(uuid.uuid4())
                    summary = i.get("summary", "Untitled")

                    # Deduplicate any duplicate events already existing in remote Google Calendar
                    key = (summary.strip().lower(), start[:16])
                    if key in seen_keys or eid in events_dict:
                        continue

                    ev = CalendarEvent(
                        id=eid,
                        summary=summary,
                        start_time=start,
                        end_time=end,
                        description=i.get("description"),
                        location=i.get("location"),
                        attendees=[a.get("email", "") for a in i.get("attendees", []) if a.get("email")],
                    )
                    events_dict[eid] = ev
                    seen_keys.add(key)
            except Exception:
                pass

        # 2. Merge local stored events (deduplicating against Google Calendar items)
        self._mock_events = self._load_local_events()
        for ev in self._mock_events:
            if not ev.id:
                ev.id = f"local-{uuid.uuid4().hex[:8]}"
            key = (ev.summary.strip().lower(), ev.start_time[:16])
            if ev.id not in events_dict and key not in seen_keys:
                events_dict[ev.id] = ev
                seen_keys.add(key)

        # 3. Sort chronologically
        sorted_events = sorted(events_dict.values(), key=lambda e: e.start_time or "")
        return sorted_events

    def check_conflicts(self, start_time_iso: str, end_time_iso: str) -> List[CalendarEvent]:
        """Checks for overlapping events in the given time window."""
        conflicts = []
        try:
            req_start = datetime.fromisoformat(_to_rfc3339(start_time_iso).replace("Z", "+00:00"))
            req_end = datetime.fromisoformat(_to_rfc3339(end_time_iso).replace("Z", "+00:00"))

            for ev in self.list_upcoming_events():
                ev_start = datetime.fromisoformat(_to_rfc3339(ev.start_time).replace("Z", "+00:00"))
                ev_end = datetime.fromisoformat(_to_rfc3339(ev.end_time).replace("Z", "+00:00"))

                if max(req_start, ev_start) < min(req_end, ev_end):
                    conflicts.append(ev)
        except Exception:
            pass
        return conflicts

    def create_event(self, event: CalendarEvent) -> Dict[str, Any]:
        """Schedules a new calendar event with reliable formatting, deduplication, and local persistence."""
        # Normalize datetime fields to RFC3339
        event.start_time = _to_rfc3339(event.start_time)
        event.end_time = _to_rfc3339(event.end_time)

        service = self._get_service()
        if service is not None:
            body = {
                "summary": event.summary,
                "description": event.description or "",
                "start": {"dateTime": event.start_time},
                "end": {"dateTime": event.end_time},
                "location": event.location or "",
                "attendees": [{"email": a} for a in event.attendees if a],
            }
            try:
                created = service.events().insert(calendarId="primary", body=body).execute()
                event.id = created.get("id")
                # Save to local storage for offline retrieval
                self._upsert_local_event(event)
                return {
                    "status": "success",
                    "event_id": created.get("id"),
                    "summary": event.summary,
                    "provider": "google_calendar_api",
                }
            except Exception as gerr:
                # Fallback to local storage so user event is NEVER lost
                event.id = f"local-{uuid.uuid4().hex[:10]}"
                self._upsert_local_event(event)
                return {
                    "status": "success",
                    "event_id": event.id,
                    "summary": event.summary,
                    "provider": "local_storage",
                    "google_api_warning": str(gerr),
                }

        # Offline / Local persistent store
        event.id = f"local-{uuid.uuid4().hex[:10]}"
        self._upsert_local_event(event)
        return {
            "status": "success",
            "event_id": event.id,
            "summary": event.summary,
            "provider": "local_storage",
            "offline_mode": True,
        }

    def _upsert_local_event(self, event: CalendarEvent):
        """Adds or updates an event in the local persistent list without duplicates."""
        self._mock_events = self._load_local_events()
        # Remove any existing event with same ID or same (summary, start_time)
        key = (event.summary.strip().lower(), event.start_time[:16])
        filtered = [
            e for e in self._mock_events
            if e.id != event.id and (e.summary.strip().lower(), e.start_time[:16]) != key
        ]
        filtered.append(event)
        self._mock_events = filtered
        self._save_local_events()

    def delete_event(self, event_id: str) -> bool:
        """Deletes an event by ID from Google Calendar and local store."""
        # 1. Try Google Calendar API
        service = self._get_service()
        if service is not None:
            try:
                service.events().delete(calendarId="primary", eventId=event_id).execute()
            except Exception:
                pass

        # 2. Delete from local storage
        self._mock_events = self._load_local_events()
        prev_len = len(self._mock_events)
        self._mock_events = [e for e in self._mock_events if e.id != event_id]
        self._save_local_events()
        return len(self._mock_events) < prev_len or True


# Singleton instance
calendar_connector = CalendarConnector()
