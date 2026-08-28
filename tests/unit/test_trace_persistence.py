"""Unit tests for SQLite-backed Execution Trace persistence and real-time listeners."""

import json
from pathlib import Path
from execution.orchestration.trace_manager import TraceStore, ExecutionTrace, TraceNodeStep


def test_trace_store_lifecycle_and_persistence(tmp_path: Path):
    db_file = tmp_path / "test_traces.sqlite3"
    store = TraceStore(db_path=db_file)

    events_received = []
    store.add_listener(lambda ev, data: events_received.append((ev, data)))

    # 1. Start trace
    trace = store.start_trace(query="Schedule a sync with Sarah", thread_id="thread-test-1", sender="user")
    assert trace.run_id is not None
    assert trace.status == "RUNNING"
    assert len(events_received) == 1
    assert events_received[0][0] == "trace_started"

    # 2. Record DAG node steps
    step1 = store.record_node_step(
        run_id=trace.run_id,
        node_name="quarantine_node",
        inputs={"raw_text": "Schedule a sync with Sarah"},
        outputs={"clean_facts": {"intent": "calendar_schedule"}},
        duration_ms=12.5,
        status="COMPLETED",
    )
    assert step1 is not None
    assert len(events_received) == 2
    assert events_received[1][0] == "node_step"

    step2 = store.record_node_step(
        run_id=trace.run_id,
        node_name="tool_execution_node",
        inputs={"tool": "calendar.create_event"},
        outputs={"status": "success"},
        duration_ms=35.0,
        status="COMPLETED",
        tool_call="calendar.create_event",
        tool_args={"summary": "Sync with Sarah", "start_time": "2026-08-28T15:00:00Z"},
    )
    assert step2 is not None

    # 3. Complete trace
    completed = store.complete_trace(
        run_id=trace.run_id,
        status="SUCCESS",
        final_output="Scheduled sync with Sarah.",
        planned_tool="calendar.create_event",
        tool_args={"summary": "Sync with Sarah"},
    )
    assert completed is not None
    assert completed.status == "SUCCESS"
    assert completed.total_duration_ms > 0
    assert len(completed.nodes) == 2

    # 4. Verify durable reload across a fresh TraceStore instance reading SQLite
    fresh_store = TraceStore(db_path=db_file)
    loaded_trace = fresh_store.get_trace(trace.run_id)
    assert loaded_trace is not None
    assert loaded_trace.run_id == trace.run_id
    assert loaded_trace.query == "Schedule a sync with Sarah"
    assert loaded_trace.status == "SUCCESS"
    assert len(loaded_trace.nodes) == 2
    assert loaded_trace.nodes[0].node_name == "quarantine_node"
    assert loaded_trace.nodes[1].tool_call == "calendar.create_event"
