"""Proactive Executive Scheduler and Background Daemons for SovereignOS.

Runs background loops for autonomous morning briefings, periodic inbox triage,
and system health telemetry without requiring manual user prompts.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("SovereignOS.Scheduler")
logger.setLevel(logging.INFO)

BRIEFING_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "latest_briefing.json"


class ExecutiveScheduler:
    """Async background task manager and executive autonomous daemon."""

    def __init__(self):
        self.is_running = False
        self._briefing_task: Optional[asyncio.Task] = None
        self._triage_task: Optional[asyncio.Task] = None
        self.briefing_interval_seconds = 3600 * 6  # Check every 6 hours or schedule at 7:30 AM
        self.triage_interval_seconds = 900         # Check inbox every 15 minutes
        self.last_briefing_time: Optional[str] = None
        self.last_triage_time: Optional[str] = None
        self.latest_briefing: Dict[str, Any] = self._load_latest_briefing()

    def _load_latest_briefing(self) -> Dict[str, Any]:
        """Loads cached executive briefing from disk."""
        if BRIEFING_PATH.exists():
            try:
                with open(BRIEFING_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load cached briefing: {e}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "headline": "SovereignOS Executive Intelligence Initialized",
            "summary": "Autonomous daemons are standing by. Ready to compile full daily briefings.",
            "metrics": {"unread_emails": 0, "today_events": 0, "active_projects": 1},
            "action_items": ["Review SovereignOS system status", "Check active MCP connectors"],
        }

    def _save_latest_briefing(self):
        """Saves current briefing to disk."""
        BRIEFING_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(BRIEFING_PATH, "w", encoding="utf-8") as f:
                json.dump(self.latest_briefing, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save briefing: {e}")

    async def start(self):
        """Starts background daemons."""
        if self.is_running:
            return
        self.is_running = True
        self._briefing_task = asyncio.create_task(self._briefing_loop())
        self._triage_task = asyncio.create_task(self._triage_loop())
        logger.info("ExecutiveScheduler background daemons started.")

    async def stop(self):
        """Stops background daemons."""
        self.is_running = False
        if self._briefing_task:
            self._briefing_task.cancel()
        if self._triage_task:
            self._triage_task.cancel()
        logger.info("ExecutiveScheduler background daemons stopped.")

    async def _briefing_loop(self):
        """Background loop that periodically checks and updates the executive briefing."""
        while self.is_running:
            try:
                await self.generate_executive_briefing()
                await asyncio.sleep(self.briefing_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in briefing loop: {e}")
                await asyncio.sleep(60)

    async def _triage_loop(self):
        """Background loop for periodic inbox triage check."""
        while self.is_running:
            try:
                await self.run_inbox_triage_check()
                await asyncio.sleep(self.triage_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in triage loop: {e}")
                await asyncio.sleep(60)

    async def generate_executive_briefing(self) -> Dict[str, Any]:
        """Synthesizes emails, calendar events, active projects, and notes into an executive brief."""
        now = datetime.now()
        iso_now = datetime.now(timezone.utc).isoformat()
        self.last_briefing_time = iso_now

        # 1. Fetch Calendar events
        today_events_count = 0
        events_summary = []
        try:
            from execution.tools.calendar_connector import calendar_connector
            events = calendar_connector.list_events(max_results=5)
            if isinstance(events, list):
                today_events_count = len(events)
                for ev in events[:3]:
                    summary = ev.get("summary") or "Scheduled Event"
                    start = ev.get("start", {}).get("dateTime", "")[:16].replace("T", " ")
                    events_summary.append(f"{summary} ({start})")
        except Exception as e:
            logger.debug(f"Calendar check note: {e}")

        # 2. Fetch Unread Email counts
        unread_count = 0
        email_summary = []
        try:
            from execution.tools.gmail_connector import gmail_connector
            unreads = gmail_connector.list_unread_emails(max_results=5)
            if isinstance(unreads, list):
                unread_count = len(unreads)
                for m in unreads[:3]:
                    subj = m.get("subject", "No subject")
                    snd = m.get("sender", "Unknown")
                    email_summary.append(f"{subj} from {snd}")
        except Exception as e:
            logger.debug(f"Gmail check note: {e}")

        # 3. Fetch Memory Graph Context
        active_projects_count = 1
        try:
            from execution.ml.memory_graph import memory_graph
            mems = memory_graph.get_all_memories(category="project")
            active_projects_count = max(len(mems), 1)
        except Exception:
            pass

        # 4. Synthesize Headline & Key Action Items
        date_str = now.strftime("%A, %B %d, %Y")
        headline = f"Executive Morning Intelligence — {date_str}"

        actions = []
        if unread_count > 0:
            actions.append(f"Triage {unread_count} pending inbox messages in Triage Room")
        if today_events_count > 0:
            actions.append(f"Prepare for {today_events_count} upcoming calendar meetings")
        actions.append("Review SovereignOS autonomous memory graph & active MCP plugins")

        summary = (
            f"Good day, Sovereign Architect. Systems are operational across all cores. "
            f"You have {unread_count} unread communications and {today_events_count} scheduled commitments today."
        )

        briefing = {
            "timestamp": iso_now,
            "date": date_str,
            "headline": headline,
            "summary": summary,
            "metrics": {
                "unread_emails": unread_count,
                "today_events": today_events_count,
                "active_projects": active_projects_count,
            },
            "events_preview": events_summary,
            "emails_preview": email_summary,
            "action_items": actions,
        }

        self.latest_briefing = briefing
        self._save_latest_briefing()

        # Record to memory graph
        try:
            from execution.ml.memory_graph import memory_graph
            memory_graph.record_event("executive_briefing", headline, {"unread": unread_count, "events": today_events_count})
        except Exception:
            pass

        return briefing

    async def run_inbox_triage_check(self) -> Dict[str, Any]:
        """Performs a background scan of unread communications."""
        iso_now = datetime.now(timezone.utc).isoformat()
        self.last_triage_time = iso_now
        status = {"status": "ok", "timestamp": iso_now, "new_urgent_count": 0}
        try:
            from execution.tools.gmail_connector import gmail_connector
            unreads = gmail_connector.list_unread_emails(max_results=10)
            status["unread_count"] = len(unreads) if isinstance(unreads, list) else 0
        except Exception as e:
            status["error"] = str(e)
        return status

    def get_status(self) -> Dict[str, Any]:
        """Returns operational status of all background daemons."""
        return {
            "is_running": self.is_running,
            "last_briefing_time": self.last_briefing_time,
            "last_triage_time": self.last_triage_time,
            "briefing_interval_hours": self.briefing_interval_seconds / 3600,
            "triage_interval_minutes": self.triage_interval_seconds / 60,
        }


# Singleton instance
executive_scheduler = ExecutiveScheduler()
