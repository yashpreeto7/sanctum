"""Execution Trace Manager with SQLite Persistence for LangSmith-style Step-by-Step Tool and Node Inspection."""

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "traces.sqlite3"


class TraceNodeStep(BaseModel):
    """Represents the execution of a single LangGraph node."""

    node_name: str
    status: str = "COMPLETED"  # RUNNING, COMPLETED, GATED, ERROR, SKIPPED
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    tool_call: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ExecutionTrace(BaseModel):
    """Container for an entire workflow run trace."""

    run_id: str = Field(default_factory=lambda: f"run-{uuid.uuid4().hex[:8]}")
    thread_id: str
    query: str
    sender: str = "user"
    status: str = "RUNNING"  # RUNNING, SUCCESS, AWAITING_APPROVAL, ERROR
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    total_duration_ms: float = 0.0
    nodes: List[TraceNodeStep] = Field(default_factory=list)
    planned_tool: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    approval_required: bool = False
    approval_request_id: Optional[str] = None
    final_output: str = ""
    error: Optional[str] = None


class TraceStore:
    """Thread-safe SQLite-backed trace store holding full persistent execution runs."""

    def __init__(self, db_path: Optional[Path] = None, max_in_memory: int = 150):
        self.db_path = db_path or DB_PATH
        self.max_in_memory = max_in_memory
        self._traces: Dict[str, ExecutionTrace] = {}
        self._ordered_ids: List[str] = []
        self._listeners: List[Callable[[str, Dict[str, Any]], None]] = []
        self._init_db()
        self._load_recent_traces()

    def add_listener(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Register a callback for real-time trace events (e.g. WebSocket streamer)."""
        self._listeners.append(callback)

    def _notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """Dispatches event to registered listeners safely."""
        for cb in list(self._listeners):
            try:
                cb(event_type, data)
            except Exception:
                pass

    def _get_connection(self) -> sqlite3.Connection:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_traces (
                    run_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    total_duration_ms REAL DEFAULT 0.0,
                    nodes_json TEXT NOT NULL DEFAULT '[]',
                    planned_tool TEXT,
                    tool_args_json TEXT,
                    approval_required INTEGER DEFAULT 0,
                    approval_request_id TEXT,
                    final_output TEXT DEFAULT '',
                    error TEXT
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_traces_start_time ON execution_traces(start_time DESC);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_traces_thread_id ON execution_traces(thread_id);")

    def _load_recent_traces(self) -> None:
        """Loads the most recent traces from SQLite into the fast in-memory cache on startup."""
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT run_id, thread_id, query, sender, status, start_time, end_time,
                           total_duration_ms, nodes_json, planned_tool, tool_args_json,
                           approval_required, approval_request_id, final_output, error
                    FROM execution_traces
                    ORDER BY start_time DESC
                    LIMIT ?
                    """,
                    (self.max_in_memory,),
                )
                rows = cur.fetchall()
                for r in rows:
                    nodes = []
                    try:
                        raw_nodes = json.loads(r["nodes_json"] or "[]")
                        nodes = [TraceNodeStep(**n) for n in raw_nodes]
                    except Exception:
                        pass
                    
                    tool_args = None
                    if r["tool_args_json"]:
                        try:
                            tool_args = json.loads(r["tool_args_json"])
                        except Exception:
                            pass

                    trace = ExecutionTrace(
                        run_id=r["run_id"],
                        thread_id=r["thread_id"],
                        query=r["query"],
                        sender=r["sender"],
                        status=r["status"],
                        start_time=r["start_time"],
                        end_time=r["end_time"],
                        total_duration_ms=r["total_duration_ms"] or 0.0,
                        nodes=nodes,
                        planned_tool=r["planned_tool"],
                        tool_args=tool_args,
                        approval_required=bool(r["approval_required"]),
                        approval_request_id=r["approval_request_id"],
                        final_output=r["final_output"] or "",
                        error=r["error"],
                    )
                    self._traces[trace.run_id] = trace
                    self._ordered_ids.append(trace.run_id)
        except Exception:
            pass

    def _save_trace_to_db(self, trace: ExecutionTrace) -> None:
        """Persists or updates a trace row in SQLite."""
        try:
            nodes_json = json.dumps([n.model_dump() for n in trace.nodes])
            tool_args_json = json.dumps(trace.tool_args) if trace.tool_args else None
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO execution_traces (
                        run_id, thread_id, query, sender, status, start_time, end_time,
                        total_duration_ms, nodes_json, planned_tool, tool_args_json,
                        approval_required, approval_request_id, final_output, error
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(run_id) DO UPDATE SET
                        status=excluded.status,
                        end_time=excluded.end_time,
                        total_duration_ms=excluded.total_duration_ms,
                        nodes_json=excluded.nodes_json,
                        planned_tool=excluded.planned_tool,
                        tool_args_json=excluded.tool_args_json,
                        approval_required=excluded.approval_required,
                        approval_request_id=excluded.approval_request_id,
                        final_output=excluded.final_output,
                        error=excluded.error
                    """,
                    (
                        trace.run_id,
                        trace.thread_id,
                        trace.query,
                        trace.sender,
                        trace.status,
                        trace.start_time,
                        trace.end_time,
                        trace.total_duration_ms,
                        nodes_json,
                        trace.planned_tool,
                        tool_args_json,
                        int(trace.approval_required),
                        trace.approval_request_id,
                        trace.final_output,
                        trace.error,
                    ),
                )
        except Exception:
            pass

    def start_trace(self, query: str, thread_id: str, sender: str = "user") -> ExecutionTrace:
        trace = ExecutionTrace(
            thread_id=thread_id,
            query=query,
            sender=sender,
        )
        self._traces[trace.run_id] = trace
        self._ordered_ids.insert(0, trace.run_id)
        if len(self._ordered_ids) > self.max_in_memory:
            oldest = self._ordered_ids.pop()
            self._traces.pop(oldest, None)

        self._save_trace_to_db(trace)
        self._notify("trace_started", {"trace": trace.model_dump()})
        return trace

    def record_node_step(
        self,
        run_id: str,
        node_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        duration_ms: float,
        status: str = "COMPLETED",
        tool_call: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Optional[TraceNodeStep]:
        trace = self._traces.get(run_id)
        if not trace:
            return None

        step = TraceNodeStep(
            node_name=node_name,
            status=status,
            duration_ms=round(duration_ms, 2),
            inputs=inputs,
            outputs=outputs,
            tool_call=tool_call,
            tool_args=tool_args,
            error=error,
        )
        trace.nodes.append(step)
        self._save_trace_to_db(trace)
        self._notify("node_step", {
            "run_id": run_id,
            "step": step.model_dump(),
            "node_name": node_name,
            "status": status,
            "duration_ms": step.duration_ms,
            "total_nodes": len(trace.nodes),
        })
        return step

    def complete_trace(
        self,
        run_id: str,
        status: str = "SUCCESS",
        final_output: str = "",
        planned_tool: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        approval_required: bool = False,
        approval_request_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[ExecutionTrace]:
        trace = self._traces.get(run_id)
        if not trace:
            return None

        trace.end_time = time.time()
        trace.total_duration_ms = round((trace.end_time - trace.start_time) * 1000.0, 2)
        trace.status = status
        trace.final_output = final_output
        trace.planned_tool = planned_tool
        trace.tool_args = tool_args
        trace.approval_required = approval_required
        trace.approval_request_id = approval_request_id
        trace.error = error

        self._save_trace_to_db(trace)
        self._notify("trace_completed", {"trace": trace.model_dump()})
        return trace

    def get_trace(self, run_id: str) -> Optional[ExecutionTrace]:
        if run_id in self._traces:
            return self._traces[run_id]
        
        # Query SQLite if not in fast memory cache
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT run_id, thread_id, query, sender, status, start_time, end_time,
                           total_duration_ms, nodes_json, planned_tool, tool_args_json,
                           approval_required, approval_request_id, final_output, error
                    FROM execution_traces WHERE run_id = ?
                    """,
                    (run_id,),
                )
                r = cur.fetchone()
                if r:
                    nodes = []
                    try:
                        raw_nodes = json.loads(r["nodes_json"] or "[]")
                        nodes = [TraceNodeStep(**n) for n in raw_nodes]
                    except Exception:
                        pass
                    
                    tool_args = None
                    if r["tool_args_json"]:
                        try:
                            tool_args = json.loads(r["tool_args_json"])
                        except Exception:
                            pass

                    return ExecutionTrace(
                        run_id=r["run_id"],
                        thread_id=r["thread_id"],
                        query=r["query"],
                        sender=r["sender"],
                        status=r["status"],
                        start_time=r["start_time"],
                        end_time=r["end_time"],
                        total_duration_ms=r["total_duration_ms"] or 0.0,
                        nodes=nodes,
                        planned_tool=r["planned_tool"],
                        tool_args=tool_args,
                        approval_required=bool(r["approval_required"]),
                        approval_request_id=r["approval_request_id"],
                        final_output=r["final_output"] or "",
                        error=r["error"],
                    )
        except Exception:
            pass
        return None

    def list_traces(self) -> List[ExecutionTrace]:
        return [self._traces[rid] for rid in self._ordered_ids if rid in self._traces]


trace_store = TraceStore()
