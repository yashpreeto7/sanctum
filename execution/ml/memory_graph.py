"""Persistent Episodic & Semantic Memory Graph for SovereignOS (Mem0-Style).

Provides local SQLite-backed entity extraction, user preference tracking, episodic
event timeline, and zero-latency context injection into LLM system prompts.
"""

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("SovereignOS.MemoryGraph")
logger.setLevel(logging.INFO)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "memory_graph.sqlite"


class MemoryGraph:
    """Manages long-term semantic facts, user preferences, and episodic events."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes database schema if not present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity TEXT NOT NULL,
                    attribute TEXT NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'preference',
                    confidence REAL NOT NULL DEFAULT 1.0,
                    source TEXT NOT NULL DEFAULT 'manual',
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(entity, attribute)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodic_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

        # Seed initial core memories if empty
        if self.count_memories() == 0:
            self._seed_default_memories()

    def _seed_default_memories(self):
        """Seeds default operational facts for SovereignOS."""
        defaults = [
            ("user", "name", "Yashpreet", "personal", "system"),
            ("user", "communication_style", "concise, direct, highly technical, markdown-formatted", "preference", "system"),
            ("user", "design_philosophy", "Old Regime editorial aesthetic, 0px sharp architectural borders, tactile physics", "preference", "system"),
            ("system", "os_codename", "SovereignOS", "system", "system"),
            ("system", "primary_local_model", "deepseek-r1:7b (Ollama)", "system", "system"),
            ("system", "default_workspace", "c:/Users/Yashpreet_o7/Desktop/PERSONALAGENT", "project", "system"),
        ]
        for entity, attr, val, cat, src in defaults:
            self.add_or_update_memory(entity, attr, val, category=cat, source=src)

    def count_memories(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute("SELECT COUNT(*) as c FROM memories").fetchone()
            return res["c"] if res else 0

    def add_or_update_memory(
        self,
        entity: str,
        attribute: str,
        value: str,
        category: str = "preference",
        confidence: float = 1.0,
        source: str = "chat",
    ) -> Dict[str, Any]:
        """Upserts a semantic fact into memory."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memories (entity, attribute, value, category, confidence, source, created_at, last_accessed_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(entity, attribute) DO UPDATE SET
                    value=excluded.value,
                    category=excluded.category,
                    confidence=excluded.confidence,
                    source=excluded.source,
                    last_accessed_at=excluded.last_accessed_at
            """, (entity.strip().lower(), attribute.strip().lower(), value.strip(), category.lower(), confidence, source, now, now))
            conn.commit()

            row = cursor.execute(
                "SELECT * FROM memories WHERE entity=? AND attribute=?",
                (entity.strip().lower(), attribute.strip().lower())
            ).fetchone()
            return dict(row) if row else {}

    def delete_memory(self, memory_id: int) -> bool:
        """Deletes a memory by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE id=?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_memories(self, category: Optional[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
        """Retrieves list of memories with optional category filter."""
        with self._get_connection() as conn:
            if category:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE category=? ORDER BY last_accessed_at DESC LIMIT ?",
                    (category.lower(), limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM memories ORDER BY last_accessed_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [dict(r) for r in rows]

    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Searches memories using multi-token matching and updates access counters."""
        tokens = [t.strip().lower() for t in query.split() if len(t.strip()) > 2]
        now = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            if not tokens:
                rows = conn.execute("SELECT * FROM memories ORDER BY access_count DESC, last_accessed_at DESC LIMIT ?", (limit,)).fetchall()
            else:
                like_clauses = " OR ".join(["entity LIKE ? OR attribute LIKE ? OR value LIKE ? OR category LIKE ?"] * len(tokens))
                params = []
                for t in tokens:
                    p = f"%{t}%"
                    params.extend([p, p, p, p])
                params.append(limit)

                sql = f"SELECT * FROM memories WHERE {like_clauses} ORDER BY access_count DESC, last_accessed_at DESC LIMIT ?"
                rows = conn.execute(sql, params).fetchall()

            results = [dict(r) for r in rows]

            # Increment access counts
            if results:
                ids = [r["id"] for r in results]
                placeholders = ",".join("?" * len(ids))
                conn.execute(
                    f"UPDATE memories SET access_count = access_count + 1, last_accessed_at = ? WHERE id IN ({placeholders})",
                    [now] + ids
                )
                conn.commit()

            return results

    def record_event(self, event_type: str, summary: str, details: Optional[Dict[str, Any]] = None):
        """Appends an event to the episodic timeline."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO episodic_events (event_type, summary, details, timestamp) VALUES (?, ?, ?, ?)",
                (event_type, summary, json.dumps(details or {}), now)
            )
            conn.commit()

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent episodic timeline events."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM episodic_events ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
            results = []
            for r in rows:
                item = dict(r)
                if item.get("details"):
                    try:
                        item["details"] = json.loads(item["details"])
                    except Exception:
                        pass
                results.append(item)
            return results

    def extract_memories_from_text(self, text: str, source: str = "chat") -> List[Dict[str, Any]]:
        """Lightweight heuristic & pattern extractor for user preferences and facts."""
        extracted = []
        text_lower = text.lower()

        # Preference patterns: "I prefer X", "I like X", "My favorite X is Y", "Always use X", "Never use X"
        import re
        patterns = [
            (r"(?:i prefer|i like|i love)\s+([a-zA-Z0-9_\-\s]{3,40})", "user", "preference", "preference"),
            (r"(?:my name is|call me)\s+([a-zA-Z0-9_\-\s]{2,20})", "user", "name", "personal"),
            (r"(?:my role is|i am an?|i work as an?)\s+([a-zA-Z0-9_\-\s]{3,30})", "user", "profession", "personal"),
            (r"(?:my project is|the project is called|working on)\s+([a-zA-Z0-9_\-\s]{3,30})", "project", "active_project", "project"),
            (r"(?:theme is|set theme to)\s+([a-zA-Z0-9_\-\s]{3,25})", "user", "preferred_theme", "preference"),
        ]

        for pat, ent, attr, cat in patterns:
            match = re.search(pat, text_lower)
            if match:
                val = match.group(1).strip()
                res = self.add_or_update_memory(ent, attr, val, category=cat, source=source)
                if res:
                    extracted.append(res)

        return extracted

    def get_context_for_prompt(self, query: str = "", max_items: int = 8) -> str:
        """Formats the top relevant memories into a clean markdown snippet for LLM prompts."""
        if query:
            memories = self.search_memories(query, limit=max_items)
        else:
            memories = self.get_all_memories(limit=max_items)

        if not memories:
            return ""

        lines = ["<persistent_memory_context>"]
        for m in memories:
            lines.append(f"- [{m['category'].upper()}] {m['entity']}.{m['attribute']}: \"{m['value']}\"")
        lines.append("</persistent_memory_context>")
        return "\n".join(lines)


# Singleton instance
memory_graph = MemoryGraph()
