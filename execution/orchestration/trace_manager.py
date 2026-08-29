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
            conn.commit()

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

        # If store is fresh or empty, seed baseline traces so LangSmith inspector is always populated
        if not self._ordered_ids:
            self._seed_baseline_traces()

    def _seed_baseline_traces(self) -> None:
        """Seeds realistic initial execution traces for testing and demonstration."""
        now = time.time()
        
        # 1. RAG Synthesis Trace
        t1 = ExecutionTrace(
            run_id="run-rag-sample",
            thread_id="thread-rag-demo",
            query="Explain Personal AI OS multi-agent architecture and quarantine security",
            sender="user",
            status="SUCCESS",
            start_time=now - 300,
            end_time=now - 299.7,
            total_duration_ms=312.4,
            planned_tool="none",
            final_output="The Personal AI OS uses a 3-layer architecture: Directives, Orchestration (LangGraph), and isolated Execution tools with Dual-LLM quarantine sanitization.",
            nodes=[
                TraceNodeStep(node_name="quarantine_node", status="COMPLETED", start_time=now - 300, end_time=now - 299.96, duration_ms=38.2, inputs={"raw_prompt": "Explain architecture"}, outputs={"clean_facts": {"topic": "architecture_security"}}),
                TraceNodeStep(node_name="triaging_node", status="COMPLETED", start_time=now - 299.96, end_time=now - 299.94, duration_ms=18.5, inputs={"topic": "architecture"}, outputs={"priority_score": 0.82, "category": "important"}),
                TraceNodeStep(node_name="retrieval_node", status="COMPLETED", start_time=now - 299.94, end_time=now - 299.86, duration_ms=81.0, inputs={"query": "multi-agent quarantine"}, outputs={"matches_count": 3, "sources": ["personal_ai_os_guide.txt"]}),
                TraceNodeStep(node_name="reasoning_node", status="COMPLETED", start_time=now - 299.86, end_time=now - 299.70, duration_ms=174.7, inputs={"retrieved_chunks": 3}, outputs={"synthesis": "Multi-agent LangGraph with 3-tier isolation."}),
            ]
        )
        self._traces[t1.run_id] = t1
        self._ordered_ids.append(t1.run_id)
        self._save_trace_to_db(t1)

        # 2. Calendar Event Trace
        t2 = ExecutionTrace(
            run_id="run-cal-sample",
            thread_id="thread-cal-demo",
            query="Schedule team sync with Alex tomorrow at 3pm",
            sender="user",
            status="SUCCESS",
            start_time=now - 600,
            end_time=now - 599.6,
            total_duration_ms=385.0,
            planned_tool="calendar.create_event",
            tool_args={"summary": "Team sync with Alex", "start_time": "2026-08-29T15:00:00"},
            final_output="✅ Calendar event 'Team sync with Alex' scheduled for tomorrow at 3:00 PM.",
            nodes=[
                TraceNodeStep(node_name="quarantine_node", status="COMPLETED", start_time=now - 600, end_time=now - 599.96, duration_ms=41.0, inputs={"raw_prompt": "Schedule team sync with Alex"}, outputs={"clean_facts": {"summary": "Team sync with Alex"}}),
                TraceNodeStep(node_name="triaging_node", status="COMPLETED", start_time=now - 599.96, end_time=now - 599.94, duration_ms=16.0, inputs={"summary": "Team sync"}, outputs={"priority_score": 0.90, "category": "important"}),
                TraceNodeStep(node_name="retrieval_node", status="COMPLETED", start_time=now - 599.94, end_time=now - 599.88, duration_ms=58.0, inputs={"query": "Alex contact"}, outputs={"matches_count": 1}),
                TraceNodeStep(node_name="reasoning_node", status="COMPLETED", start_time=now - 599.88, end_time=now - 599.72, duration_ms=160.0, inputs={"intent": "schedule"}, outputs={"tool": "calendar.create_event"}),
                TraceNodeStep(node_name="approval_gate_node", status="COMPLETED", start_time=now - 599.72, end_time=now - 599.71, duration_ms=2.0, inputs={"tool_name": "calendar.create_event"}, outputs={"status": "AUTO_APPROVED"}),
                TraceNodeStep(node_name="tool_execution_node", status="COMPLETED", start_time=now - 599.71, end_time=now - 599.60, duration_ms=108.0, inputs={"tool_name": "calendar.create_event"}, outputs={"event_id": "ev-sample-01", "status": "confirmed"}),
            ]
        )
        self._traces[t2.run_id] = t2
        self._ordered_ids.append(t2.run_id)
        self._save_trace_to_db(t2)

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
                conn.commit()
        except Exception:
            pass

    def start_trace(self, query: str, thread_id: str, sender: str = "user", run_id: Optional[str] = None) -> ExecutionTrace:
        trace = ExecutionTrace(
            run_id=run_id or f"run-{uuid.uuid4().hex[:8]}",
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

    # Alias for convenience
    finish_trace = complete_trace


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

    def get_stats(self) -> Dict[str, Any]:
        """Calculates aggregate execution analytics across all stored traces."""
        traces = self.list_traces()
        total = len(traces)
        if total == 0:
            return {
                "total_runs": 0,
                "avg_duration_ms": 0.0,
                "success_count": 0,
                "success_rate_pct": 100.0,
                "gated_count": 0,
                "error_count": 0,
                "total_nodes_executed": 0,
                "tool_usage_counts": {},
            }

        success_count = sum(1 for t in traces if t.status == "SUCCESS")
        gated_count = sum(1 for t in traces if t.status in ("AWAITING_APPROVAL", "GATED"))
        error_count = sum(1 for t in traces if t.status == "ERROR")
        durations = [t.total_duration_ms for t in traces if t.total_duration_ms > 0]
        avg_dur = sum(durations) / len(durations) if durations else 0.0
        total_nodes = sum(len(t.nodes) for t in traces)

        tool_counts: Dict[str, int] = {}
        for t in traces:
            if t.planned_tool:
                tool_counts[t.planned_tool] = tool_counts.get(t.planned_tool, 0) + 1

        success_rate = (success_count / total) * 100.0 if total > 0 else 100.0

        return {
            "total_runs": total,
            "avg_duration_ms": round(avg_dur, 2),
            "success_count": success_count,
            "success_rate_pct": round(success_rate, 1),
            "gated_count": gated_count,
            "error_count": error_count,
            "total_nodes_executed": total_nodes,
            "tool_usage_counts": tool_counts,
        }

    def clear_traces(self) -> None:
        """Clears all execution traces from memory and SQLite."""
        self._traces.clear()
        self._ordered_ids.clear()
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM execution_traces;")
                conn.commit()
        except Exception:
            pass


trace_store = TraceStore()

