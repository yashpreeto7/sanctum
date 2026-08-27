"""Local SQLite Persistent Chat History Management System (ChatGPT-style)."""

import json
import re
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Database storage path
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "chat_history.db"


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:10]}")
    session_id: str
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: float = Field(default_factory=time.time)
    run_id: Optional[str] = None
    planned_tool: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    approval_required: bool = False
    approval_request_id: Optional[str] = None


class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: f"session-{uuid.uuid4().hex[:8]}")
    title: str = "New Chat"
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    message_count: int = 0
    pinned: bool = False
    last_message_preview: Optional[str] = None


class ChatHistoryStore:
    """Thread-safe SQLite persistent store for local multi-session chat histories."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    pinned INTEGER DEFAULT 0,
                    last_message_preview TEXT
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    run_id TEXT,
                    planned_tool TEXT,
                    tool_args TEXT,
                    approval_required INTEGER DEFAULT 0,
                    approval_request_id TEXT,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id, timestamp);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated ON chat_sessions(updated_at DESC);")

    def create_session(self, title: Optional[str] = None, session_id: Optional[str] = None) -> ChatSession:
        sid = session_id or f"session-{uuid.uuid4().hex[:8]}"
        session_title = title or "New Chat"
        now = time.time()
        session = ChatSession(
            id=sid,
            title=session_title,
            created_at=now,
            updated_at=now,
            message_count=0,
            pinned=False,
            last_message_preview="",
        )
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_sessions (id, title, created_at, updated_at, message_count, pinned, last_message_preview)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET title=excluded.title
                """,
                (session.id, session.title, session.created_at, session.updated_at, session.message_count, int(session.pinned), session.last_message_preview),
            )
        return session

    def list_sessions(self, limit: int = 100) -> List[ChatSession]:
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, title, created_at, updated_at, message_count, pinned, last_message_preview
                FROM chat_sessions
                ORDER BY pinned DESC, updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cur.fetchall()
            return [
                ChatSession(
                    id=row["id"],
                    title=row["title"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    message_count=row["message_count"],
                    pinned=bool(row["pinned"]),
                    last_message_preview=row["last_message_preview"] or "",
                )
                for row in rows
            ]

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT id, title, created_at, updated_at, message_count, pinned, last_message_preview FROM chat_sessions WHERE id = ?",
                (session_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return ChatSession(
                id=row["id"],
                title=row["title"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                message_count=row["message_count"],
                pinned=bool(row["pinned"]),
                last_message_preview=row["last_message_preview"] or "",
            )

    def update_session_title(self, session_id: str, title: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute(
                "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title.strip() or "Untitled Chat", time.time(), session_id),
            )
            return cur.rowcount > 0

    def toggle_pin_session(self, session_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute(
                "UPDATE chat_sessions SET pinned = CASE WHEN pinned = 1 THEN 0 ELSE 1 END WHERE id = ?",
                (session_id,),
            )
            return cur.rowcount > 0

    def delete_session(self, session_id: str) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            cur = conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            return cur.rowcount > 0

    def clear_all_history(self) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM chat_messages;")
            conn.execute("DELETE FROM chat_sessions;")
            return True

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        run_id: Optional[str] = None,
        planned_tool: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        approval_required: bool = False,
        approval_request_id: Optional[str] = None,
    ) -> ChatMessage:
        now = time.time()
        # Ensure session exists
        existing = self.get_session(session_id)
        if not existing:
            # Generate initial title if user message
            title = self.generate_smart_title(content) if role == "user" else "New Conversation"
            self.create_session(title=title, session_id=session_id)
        elif existing.title == "New Chat" and role == "user":
            # Auto-title on first user prompt
            new_title = self.generate_smart_title(content)
            self.update_session_title(session_id, new_title)

        msg_id = f"msg-{uuid.uuid4().hex[:10]}"
        tool_args_json = json.dumps(tool_args) if tool_args else None
        preview = content[:100].replace("\n", " ").strip()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (
                    id, session_id, role, content, timestamp, run_id, planned_tool, tool_args, approval_required, approval_request_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    msg_id,
                    session_id,
                    role,
                    content,
                    now,
                    run_id,
                    planned_tool,
                    tool_args_json,
                    int(approval_required),
                    approval_request_id,
                ),
            )
            # Update session stats
            conn.execute(
                """
                UPDATE chat_sessions
                SET updated_at = ?,
                    message_count = (SELECT COUNT(*) FROM chat_messages WHERE session_id = ?),
                    last_message_preview = ?
                WHERE id = ?
                """,
                (now, session_id, preview, session_id),
            )

        return ChatMessage(
            id=msg_id,
            session_id=session_id,
            role=role,
            content=content,
            timestamp=now,
            run_id=run_id,
            planned_tool=planned_tool,
            tool_args=tool_args,
            approval_required=approval_required,
            approval_request_id=approval_request_id,
        )

    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, session_id, role, content, timestamp, run_id, planned_tool, tool_args, approval_required, approval_request_id
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
                """,
                (session_id,),
            )
            rows = cur.fetchall()
            messages = []
            for r in rows:
                args = None
                if r["tool_args"]:
                    try:
                        args = json.loads(r["tool_args"])
                    except Exception:
                        pass
                messages.append(
                    ChatMessage(
                        id=r["id"],
                        session_id=r["session_id"],
                        role=r["role"],
                        content=r["content"],
                        timestamp=r["timestamp"],
                        run_id=r["run_id"],
                        planned_tool=r["planned_tool"],
                        tool_args=args,
                        approval_required=bool(r["approval_required"]),
                        approval_request_id=r["approval_request_id"],
                    )
                )
            return messages

    @staticmethod
    def generate_smart_title(query: str) -> str:
        """Generates a concise ChatGPT-style session title from the user's first query."""
        clean = query.strip()
        # Clean common prompt fluff
        clean = re.sub(r"^(?:please\s+|can\s+you\s+|could\s+you\s+|i\s+want\s+to\s+|help\s+me\s+)", "", clean, flags=re.IGNORECASE)
        # Check specific intent prefixes
        if re.search(r"^(?:check\s+if\s+i\s+rec[ei]+ved|search\s+emails?|did\s+i\s+get)", clean, re.IGNORECASE):
            match = re.search(r"from\s+([\w\.-]+@[\w\.-]+\.\w+|\w+)", clean, re.IGNORECASE)
            if match:
                return f"Emails from {match.group(1)}"
            return "Search Inbound Emails"
        if re.search(r"^(?:send\s+(?:an?\s+)?(?:email|mail)|write\s+email)", clean, re.IGNORECASE):
            match = re.search(r"to\s+([\w\.-]+@[\w\.-]+\.\w+|\w+)", clean, re.IGNORECASE)
            if match:
                return f"Email to {match.group(1)}"
            return "Send Outbound Email"
        if re.search(r"^(?:schedule|calendar|meeting)", clean, re.IGNORECASE):
            return "Schedule Meeting"
        if re.search(r"^(?:save\s+note|take\s+note|notes?)", clean, re.IGNORECASE):
            return "Notes & Documentation"
        if re.search(r"^(?:unread|inbox|check\s+inbox)", clean, re.IGNORECASE):
            return "Inbox Triage"

        # General capitalization and truncating
        title = clean[:38].strip()
        if len(clean) > 38:
            title += "..."
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        return title or "New Conversation"


# Global persistent singleton instance
chat_history_store = ChatHistoryStore()
