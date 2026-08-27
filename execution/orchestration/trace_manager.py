"""Execution Trace Manager for LangSmith-style Step-by-Step Tool and Node Inspection."""

import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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
    """In-memory circular trace store holding recent execution runs for inspection."""

    def __init__(self, max_runs: int = 100):
        self.max_runs = max_runs
        self._traces: Dict[str, ExecutionTrace] = {}
        self._ordered_ids: List[str] = []

    def start_trace(self, query: str, thread_id: str, sender: str = "user") -> ExecutionTrace:
        trace = ExecutionTrace(
            thread_id=thread_id,
            query=query,
            sender=sender,
        )
        self._traces[trace.run_id] = trace
        self._ordered_ids.insert(0, trace.run_id)
        if len(self._ordered_ids) > self.max_runs:
            oldest = self._ordered_ids.pop()
            self._traces.pop(oldest, None)
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
        return trace

    def get_trace(self, run_id: str) -> Optional[ExecutionTrace]:
        return self._traces.get(run_id)

    def list_traces(self) -> List[ExecutionTrace]:
        return [self._traces[rid] for rid in self._ordered_ids if rid in self._traces]


trace_store = TraceStore()
