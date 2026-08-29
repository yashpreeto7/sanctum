"""Deterministic Calendar Tool supporting live Google Calendar API, past/future schedule retrieval, and cultural festival tracking."""

import json
import os
import uuid
import time
from datetime import datetime, timedelta, timezone
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
    event_type: str = Field(default="schedule", description="'schedule', 'festival', or 'holiday'")
    emoji: Optional[str] = None
    is_all_day: bool = False


# Curated dataset of major national, cultural, and seasonal festivals
FESTIVALS_DATA: Dict[int, List[Dict[str, str]]] = {
    2025: [
        {"summary": "New Year's Day", "date": "2025-01-01", "emoji": "🎉", "description": "Global celebration of the first day of the year."},
        {"summary": "Lohri", "date": "2025-01-13", "emoji": "🔥", "description": "Punjabi winter harvest festival celebrated with bonfires and folk songs."},
        {"summary": "Makar Sankranti / Pongal", "date": "2025-01-14", "emoji": "🪁", "description": "Solar cycle harvest festival celebrated with kite flying."},
        {"summary": "Republic Day", "date": "2025-01-26", "emoji": "🇮🇳", "description": "National holiday honoring the Constitution of India."},
        {"summary": "Maha Shivratri", "date": "2025-02-26", "emoji": "🔱", "description": "Auspicious festival honoring Lord Shiva."},
        {"summary": "Holi (Festival of Colors)", "date": "2025-03-14", "emoji": "🎨", "description": "Joyous celebration of spring, love, and colors."},
        {"summary": "Eid ul-Fitr", "date": "2025-03-31", "emoji": "🌙", "description": "Islamic festival marking the end of Ramadan fast."},
        {"summary": "Baisakhi", "date": "2025-04-13", "emoji": "🌾", "description": "Spring harvest festival and Sikh New Year."},
        {"summary": "Good Friday", "date": "2025-04-18", "emoji": "✝️", "description": "Christian holiday commemorating the crucifixion of Jesus."},
        {"summary": "Easter Sunday", "date": "2025-04-20", "emoji": "🐣", "description": "Christian celebration of the resurrection of Jesus Christ."},
        {"summary": "Labour Day", "date": "2025-05-01", "emoji": "🛠️", "description": "International Workers' Day."},
        {"summary": "Eid al-Adha (Bakrid)", "date": "2025-06-07", "emoji": "🐑", "description": "Feast of the Sacrifice in Islamic tradition."},
        {"summary": "Independence Day", "date": "2025-08-15", "emoji": "🇮🇳", "description": "Commemorates the nation's independence in 1947."},
        {"summary": "Raksha Bandhan", "date": "2025-08-09", "emoji": "🧵", "description": "Celebration of sibling bond and protection."},
        {"summary": "Janmashtami", "date": "2025-08-16", "emoji": "🦚", "description": "Birth celebration of Lord Krishna."},
        {"summary": "Ganesh Chaturthi", "date": "2025-08-27", "emoji": "🐘", "description": "Festival welcoming Lord Ganesha."},
        {"summary": "Gandhi Jayanti", "date": "2025-10-02", "emoji": "🕊️", "description": "National holiday commemorating Mahatma Gandhi's birthday."},
        {"summary": "Dussehra (Vijayadashami)", "date": "2025-10-02", "emoji": "🏹", "description": "Celebration of victory over evil."},
        {"summary": "Diwali (Festival of Lights)", "date": "2025-10-20", "emoji": "🪔", "description": "Grand festival of lights, prosperity, and joy."},
        {"summary": "Bhai Dooj", "date": "2025-10-22", "emoji": "🎁", "description": "Auspicious celebration between brothers and sisters."},
        {"summary": "Guru Nanak Jayanti", "date": "2025-11-05", "emoji": "✨", "description": "Celebration of the birth of Guru Nanak Dev Ji."},
        {"summary": "Christmas Eve", "date": "2025-12-24", "emoji": "🎄", "description": "Evening preceding Christmas Day."},
        {"summary": "Christmas Day", "date": "2025-12-25", "emoji": "🎅", "description": "Celebration of the birth of Jesus Christ."},
        {"summary": "New Year's Eve", "date": "2025-12-31", "emoji": "🥂", "description": "Celebrations welcoming the new year."},
    ],
    2026: [
        {"summary": "New Year's Day", "date": "2026-01-01", "emoji": "🎉", "description": "Global celebration of the first day of the year."},
        {"summary": "Lohri", "date": "2026-01-13", "emoji": "🔥", "description": "Punjabi winter harvest festival celebrated with bonfires and folk songs."},
        {"summary": "Makar Sankranti / Pongal", "date": "2026-01-14", "emoji": "🪁", "description": "Solar cycle harvest festival celebrated with kite flying."},
        {"summary": "Republic Day", "date": "2026-01-26", "emoji": "🇮🇳", "description": "National holiday honoring the Constitution of India."},
        {"summary": "Maha Shivratri", "date": "2026-02-15", "emoji": "🔱", "description": "Auspicious festival honoring Lord Shiva."},
        {"summary": "Holi (Festival of Colors)", "date": "2026-03-03", "emoji": "🎨", "description": "Joyous celebration of spring, love, and colors."},
        {"summary": "Eid ul-Fitr", "date": "2026-03-20", "emoji": "🌙", "description": "Islamic festival marking the end of Ramadan fast."},
        {"summary": "Good Friday", "date": "2026-04-03", "emoji": "✝️", "description": "Christian holiday commemorating the crucifixion of Jesus."},
        {"summary": "Easter Sunday", "date": "2026-04-05", "emoji": "🐣", "description": "Christian celebration of the resurrection of Jesus Christ."},
        {"summary": "Baisakhi", "date": "2026-04-14", "emoji": "🌾", "description": "Spring harvest festival and Sikh New Year."},
        {"summary": "Labour Day", "date": "2026-05-01", "emoji": "🛠️", "description": "International Workers' Day."},
        {"summary": "Eid al-Adha (Bakrid)", "date": "2026-05-27", "emoji": "🐑", "description": "Feast of the Sacrifice in Islamic tradition."},
        {"summary": "Independence Day", "date": "2026-08-15", "emoji": "🇮🇳", "description": "Commemorates the nation's independence in 1947."},
        {"summary": "Raksha Bandhan", "date": "2026-08-28", "emoji": "🧵", "description": "Celebration of sibling bond and protection."},
        {"summary": "Janmashtami", "date": "2026-09-04", "emoji": "🦚", "description": "Birth celebration of Lord Krishna."},
        {"summary": "Ganesh Chaturthi", "date": "2026-09-14", "emoji": "🐘", "description": "Festival welcoming Lord Ganesha."},
        {"summary": "Gandhi Jayanti", "date": "2026-10-02", "emoji": "🕊️", "description": "National holiday commemorating Mahatma Gandhi's birthday."},
        {"summary": "Dussehra (Vijayadashami)", "date": "2026-10-20", "emoji": "🏹", "description": "Celebration of victory over evil."},
        {"summary": "Diwali (Festival of Lights)", "date": "2026-11-08", "emoji": "🪔", "description": "Grand festival of lights, prosperity, and joy."},
        {"summary": "Govardhan Puja / Bhai Dooj", "date": "2026-11-10", "emoji": "🎁", "description": "Auspicious celebration between brothers and sisters."},
        {"summary": "Guru Nanak Jayanti", "date": "2026-11-24", "emoji": "✨", "description": "Celebration of the birth of Guru Nanak Dev Ji."},
        {"summary": "Christmas Eve", "date": "2026-12-24", "emoji": "🎄", "description": "Evening preceding Christmas Day."},
        {"summary": "Christmas Day", "date": "2026-12-25", "emoji": "🎅", "description": "Celebration of the birth of Jesus Christ."},
        {"summary": "New Year's Eve", "date": "2026-12-31", "emoji": "🥂", "description": "Celebrations welcoming the new year."},
    ],
    2027: [
        {"summary": "New Year's Day", "date": "2027-01-01", "emoji": "🎉", "description": "Global celebration of the first day of the year."},
        {"summary": "Lohri", "date": "2027-01-13", "emoji": "🔥", "description": "Punjabi winter harvest festival celebrated with bonfires and folk songs."},
        {"summary": "Makar Sankranti / Pongal", "date": "2027-01-14", "emoji": "🪁", "description": "Solar cycle harvest festival celebrated with kite flying."},
        {"summary": "Republic Day", "date": "2027-01-26", "emoji": "🇮🇳", "description": "National holiday honoring the Constitution of India."},
        {"summary": "Maha Shivratri", "date": "2027-03-06", "emoji": "🔱", "description": "Auspicious festival honoring Lord Shiva."},
        {"summary": "Eid ul-Fitr", "date": "2027-03-10", "emoji": "🌙", "description": "Islamic festival marking the end of Ramadan fast."},
        {"summary": "Holi (Festival of Colors)", "date": "2027-03-22", "emoji": "🎨", "description": "Joyous celebration of spring, love, and colors."},
        {"summary": "Good Friday", "date": "2027-03-26", "emoji": "✝️", "description": "Christian holiday commemorating the crucifixion of Jesus."},
        {"summary": "Easter Sunday", "date": "2027-03-28", "emoji": "🐣", "description": "Christian celebration of the resurrection of Jesus Christ."},
        {"summary": "Baisakhi", "date": "2027-04-14", "emoji": "🌾", "description": "Spring harvest festival and Sikh New Year."},
        {"summary": "Labour Day", "date": "2027-05-01", "emoji": "🛠️", "description": "International Workers' Day."},
        {"summary": "Eid al-Adha (Bakrid)", "date": "2027-05-16", "emoji": "🐑", "description": "Feast of the Sacrifice in Islamic tradition."},
        {"summary": "Independence Day", "date": "2027-08-15", "emoji": "🇮🇳", "description": "Commemorates the nation's independence in 1947."},
        {"summary": "Raksha Bandhan", "date": "2027-08-16", "emoji": "🧵", "description": "Celebration of sibling bond and protection."},
        {"summary": "Janmashtami", "date": "2027-08-25", "emoji": "🦚", "description": "Birth celebration of Lord Krishna."},
        {"summary": "Ganesh Chaturthi", "date": "2027-09-04", "emoji": "🐘", "description": "Festival welcoming Lord Ganesha."},
        {"summary": "Gandhi Jayanti", "date": "2027-10-02", "emoji": "🕊️", "description": "National holiday commemorating Mahatma Gandhi's birthday."},
        {"summary": "Dussehra (Vijayadashami)", "date": "2027-10-10", "emoji": "🏹", "description": "Celebration of victory over evil."},
        {"summary": "Diwali (Festival of Lights)", "date": "2027-10-29", "emoji": "🪔", "description": "Grand festival of lights, prosperity, and joy."},
        {"summary": "Bhai Dooj", "date": "2027-10-31", "emoji": "🎁", "description": "Auspicious celebration between brothers and sisters."},
        {"summary": "Guru Nanak Jayanti", "date": "2027-11-14", "emoji": "✨", "description": "Celebration of the birth of Guru Nanak Dev Ji."},
        {"summary": "Christmas Day", "date": "2027-12-25", "emoji": "🎅", "description": "Celebration of the birth of Jesus Christ."},
    ]
}


def _to_rfc3339(dt_str: str) -> str:
    """Converts any datetime string (e.g. YYYY-MM-DDTHH:MM or ISO) to standard RFC3339 format."""
    if not dt_str:
        return datetime.now(timezone.utc).isoformat()
    dt_str = dt_str.strip()
    try:
        if dt_str.endswith("Z"):
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.astimezone()
        return dt.isoformat()
    except Exception:
        if len(dt_str) == 16:
            local_tz = datetime.now().astimezone().strftime("%z")
            tz_formatted = f"{local_tz[:3]}:{local_tz[3:]}" if len(local_tz) == 5 else "+00:00"
            return f"{dt_str}:00{tz_formatted}"
        return dt_str


class CalendarConnector:
    """Manages reading, past/future scheduling, deduplication, conflict detection, and festivals."""

    def __init__(self, service: Optional[Any] = None, storage_path: Optional[Path] = None):
        self._custom_service = service
        self.storage_path = storage_path or (settings.TEMP_DIR / "calendar_events.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.deleted_path = self.storage_path.parent / "calendar_deleted_ids.json"
        self._deleted_ids: set = set()
        self._deleted_keys: set = set()
        self._load_deleted()
        self._mock_events: List[CalendarEvent] = self._load_local_events()
        self._cached_events: List[CalendarEvent] = []
        self._cache_timestamp: float = 0.0
        self._cache_ttl_seconds: float = 60.0

    def _load_deleted(self):
        """Loads deleted event IDs and keys from persistent storage."""
        if not self.deleted_path.exists():
            return
        try:
            raw = json.loads(self.deleted_path.read_text(encoding="utf-8"))
            self._deleted_ids = set(raw.get("ids", []))
            self._deleted_keys = set(raw.get("keys", []))
        except Exception:
            self._deleted_ids = set()
            self._deleted_keys = set()

    def _save_deleted(self):
        """Saves deleted event IDs and keys to persistent storage."""
        try:
            data = {
                "ids": list(self._deleted_ids),
                "keys": list(self._deleted_keys),
            }
            self.deleted_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

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
            events = []
            for item in data:
                ev = CalendarEvent(**item)
                key16 = (ev.summary.strip().lower(), ev.start_time[:16])
                key10 = (ev.summary.strip().lower(), ev.start_time[:10])
                if ev.id not in self._deleted_ids and key16 not in self._deleted_keys and key10 not in self._deleted_keys:
                    events.append(ev)
            return events
        except Exception:
            return []

    def _save_local_events(self):
        """Persists local calendar events to disk."""
        try:
            raw = [e.model_dump() for e in self._mock_events]
            self.storage_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        except Exception:
            pass

    def list_festivals(self, year: Optional[int] = None) -> List[CalendarEvent]:
        """Returns festival events for the specified year or current ± 1 year range."""
        current_year = datetime.now().year
        years = [year] if year else [current_year - 1, current_year, current_year + 1]
        festivals = []

        for y in years:
            items = FESTIVALS_DATA.get(y, [])
            for item in items:
                d_str = item["date"]
                f_id = f"festival-{d_str}-{item['summary'].replace(' ', '_').lower()}"
                key10 = (item["summary"].strip().lower(), d_str[:10])
                emoji_key10 = (f"{item['emoji']} {item['summary']}".strip().lower(), d_str[:10])
                
                if f_id in self._deleted_ids or key10 in self._deleted_keys or emoji_key10 in self._deleted_keys:
                    continue

                festivals.append(
                    CalendarEvent(
                        id=f_id,
                        summary=f"{item['emoji']} {item['summary']}",
                        start_time=f"{d_str}T00:00:00",
                        end_time=f"{d_str}T23:59:59",
                        description=item["description"],
                        location="Celebrated Globally / Nationally",
                        event_type="festival",
                        emoji=item["emoji"],
                        is_all_day=True,
                    )
                )
        return sorted(festivals, key=lambda e: e.start_time)

    def list_upcoming_events(
        self,
        days_back: int = 120,
        days_ahead: int = 365,
        include_festivals: bool = True,
        force_refresh: bool = False,
    ) -> List[CalendarEvent]:
        """Lists past, present, and upcoming events with strict deduplication and deleted tombstone filtering."""
        now_ts = time.time()
        if not force_refresh and self._cached_events and (now_ts - self._cache_timestamp < self._cache_ttl_seconds):
            return self._cached_events

        self._load_deleted()
        events_dict: Dict[str, CalendarEvent] = {}
        seen_keys = set()

        # 1. Fetch Google Calendar events in wide time window (including past days)
        service = self._get_service()
        if service is not None:
            try:
                time_min = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()
                time_max = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()
                events_result = service.events().list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=250,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()
                items = events_result.get("items", [])
                for i in items:
                    start = i.get("start", {}).get("dateTime") or i.get("start", {}).get("date") or ""
                    end = i.get("end", {}).get("dateTime") or i.get("end", {}).get("date") or ""
                    eid = i.get("id") or str(uuid.uuid4())
                    summary = i.get("summary", "Untitled")

                    key = (summary.strip().lower(), start[:16])
                    key10 = (summary.strip().lower(), start[:10])
                    
                    if eid in self._deleted_ids or key in self._deleted_keys or key10 in self._deleted_keys:
                        continue
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
                        event_type="schedule",
                    )
                    events_dict[eid] = ev
                    seen_keys.add(key)
            except Exception:
                pass

        # 2. Merge local stored events (including all past and future records)
        self._mock_events = self._load_local_events()
        for ev in self._mock_events:
            if not ev.id:
                ev.id = f"local-{uuid.uuid4().hex[:8]}"
            key = (ev.summary.strip().lower(), ev.start_time[:16])
            key10 = (ev.summary.strip().lower(), ev.start_time[:10])
            
            if ev.id in self._deleted_ids or key in self._deleted_keys or key10 in self._deleted_keys:
                continue
            if ev.id not in events_dict and key not in seen_keys:
                events_dict[ev.id] = ev
                seen_keys.add(key)

        # 3. Include cultural festivals
        if include_festivals:
            for f_ev in self.list_festivals():
                key = (f_ev.summary.strip().lower(), f_ev.start_time[:10])
                if f_ev.id in self._deleted_ids or key in self._deleted_keys:
                    continue
                if f_ev.id not in events_dict and key not in seen_keys:
                    events_dict[f_ev.id] = f_ev
                    seen_keys.add(key)

        # 4. Sort chronologically
        sorted_events = sorted(events_dict.values(), key=lambda e: e.start_time or "")
        self._cached_events = sorted_events
        self._cache_timestamp = time.time()
        return sorted_events

    def check_conflicts(self, start_time_iso: str, end_time_iso: str) -> List[CalendarEvent]:
        """Checks for overlapping events in the given time window (ignoring full-day festivals)."""
        conflicts = []
        try:
            req_start = datetime.fromisoformat(_to_rfc3339(start_time_iso).replace("Z", "+00:00"))
            req_end = datetime.fromisoformat(_to_rfc3339(end_time_iso).replace("Z", "+00:00"))

            for ev in self.list_upcoming_events(days_back=7, days_ahead=30, include_festivals=False):
                if ev.event_type == "festival" or ev.is_all_day:
                    continue
                ev_start = datetime.fromisoformat(_to_rfc3339(ev.start_time).replace("Z", "+00:00"))
                ev_end = datetime.fromisoformat(_to_rfc3339(ev.end_time).replace("Z", "+00:00"))

                if max(req_start, ev_start) < min(req_end, ev_end):
                    conflicts.append(ev)
        except Exception:
            pass
        return conflicts

    def create_event(self, event: CalendarEvent) -> Dict[str, Any]:
        """Schedules a new calendar event with reliable formatting, deduplication, and local persistence."""
        event.start_time = _to_rfc3339(event.start_time)
        event.end_time = _to_rfc3339(event.end_time)
        event.event_type = "schedule"

        # If re-creating an event that was previously deleted, un-tombstone it
        key16 = (event.summary.strip().lower(), event.start_time[:16])
        key10 = (event.summary.strip().lower(), event.start_time[:10])
        self._deleted_keys.discard(key16)
        self._deleted_keys.discard(key10)
        if event.id:
            self._deleted_ids.discard(event.id)
        self._save_deleted()

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
                if event.id:
                    self._deleted_ids.discard(event.id)
                self._upsert_local_event(event)
                return {
                    "status": "success",
                    "event_id": created.get("id"),
                    "summary": event.summary,
                    "provider": "google_calendar_api",
                }
            except Exception as gerr:
                existing_id = None
                key = (event.summary.strip().lower(), event.start_time[:16])
                for e in self._load_local_events():
                    if (e.summary.strip().lower(), e.start_time[:16]) == key or e.id == event.id:
                        existing_id = e.id
                        break
                event.id = existing_id or f"local-{uuid.uuid4().hex[:10]}"
                self._upsert_local_event(event)
                return {
                    "status": "success",
                    "event_id": event.id,
                    "summary": event.summary,
                    "provider": "local_storage",
                    "google_api_warning": str(gerr),
                }

        # Check if existing event has same key to preserve its ID
        existing_id = None
        key = (event.summary.strip().lower(), event.start_time[:16])
        for e in self._load_local_events():
            if (e.summary.strip().lower(), e.start_time[:16]) == key or e.id == event.id:
                existing_id = e.id
                break

        event.id = existing_id or f"local-{uuid.uuid4().hex[:10]}"
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
        self._cache_timestamp = 0.0
        self._cached_events = []
        self._mock_events = self._load_local_events()
        key = (event.summary.strip().lower(), event.start_time[:16])
        filtered = [
            e for e in self._mock_events
            if e.id != event.id and (e.summary.strip().lower(), e.start_time[:16]) != key
        ]
        filtered.append(event)
        self._mock_events = filtered
        self._save_local_events()

    def delete_event(self, event_id: str) -> bool:
        """Deletes an event by ID from Google Calendar, local store, and records tombstone."""
        self._cache_timestamp = 0.0
        self._cached_events = []
        self._load_deleted()
        self._deleted_ids.add(event_id)

        # Look up event in local store or memory to also record its summary/date key
        target_event = None
        for e in self._load_local_events():
            if e.id == event_id:
                target_event = e
                break

        if target_event:
            self._deleted_keys.add((target_event.summary.strip().lower(), target_event.start_time[:16]))
            self._deleted_keys.add((target_event.summary.strip().lower(), target_event.start_time[:10]))

        # Also check festivals
        for f in self.list_festivals():
            if f.id == event_id:
                self._deleted_keys.add((f.summary.strip().lower(), f.start_time[:10]))
                clean_name = f.summary.split(" ", 1)[-1].strip().lower()
                self._deleted_keys.add((clean_name, f.start_time[:10]))

        self._save_deleted()

        service = self._get_service()
        if service is not None:
            try:
                service.events().delete(calendarId="primary", eventId=event_id).execute()
            except Exception:
                pass

        self._mock_events = [e for e in self._mock_events if e.id != event_id]
        self._save_local_events()
        return True


# Singleton instance
calendar_connector = CalendarConnector()
