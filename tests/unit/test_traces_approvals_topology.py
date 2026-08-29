"""Unit tests for Traces, HITL Approvals, and Topology DAG API endpoints."""

import pytest
from fastapi.testclient import TestClient
from server.app import app
from execution.orchestration.permission_manager import permission_manager
from execution.orchestration.trace_manager import trace_store


@pytest.fixture
def client():
    return TestClient(app)


def test_traces_lifecycle_and_simulation(client):
    # 1. Clear traces
    res = client.post("/api/traces/clear")
    assert res.status_code == 200

    # 2. Check stats empty
    res = client.get("/api/traces/stats")
    assert res.status_code == 200
    stats = res.json()["stats"]
    assert stats["total_runs"] == 0

    # 3. Simulate trace
    res = client.post("/api/traces/simulate", json={"scenario": "rag"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "simulated"
    assert data["run_id"].startswith("sim-")

    # 4. List traces
    res = client.get("/api/traces")
    assert res.status_code == 200
    traces = res.json()["traces"]
    assert len(traces) >= 1

    # 5. Get detail
    run_id = data["run_id"]
    res = client.get(f"/api/traces/{run_id}")
    assert res.status_code == 200
    detail = res.json()["trace"]
    assert detail["run_id"] == run_id
    assert len(detail["nodes"]) > 0


def test_approvals_simulation_policies_and_history(client):
    # 1. Simulate approval
    res = client.post("/api/approvals/simulate", json={"tool_name": "email.send"})
    assert res.status_code == 200
    req = res.json()["request"]
    assert req["tool_name"] == "email.send"
    assert req["risk_level"] == "HIGH"
    req_id = req["id"]

    # 2. List pending
    res = client.get("/api/approvals")
    assert res.status_code == 200
    pending = res.json()["pending_approvals"]
    assert any(p["id"] == req_id for p in pending)

    # 3. Resolve approval with modified args and notes
    res = client.post(
        f"/api/approvals/{req_id}/resolve",
        json={
            "approved": True,
            "modified_args": {"to": "reviewed@enterprise.com", "subject": "Approved Proposal", "body": "Approved."},
            "notes": "Reviewed and authorized by security officer.",
        },
    )
    assert res.status_code == 200
    resolved = res.json()
    assert resolved["status"] == "resolved"
    assert resolved["request"]["operator_notes"] == "Reviewed and authorized by security officer."

    # 4. Check history
    res = client.get("/api/approvals/history")
    assert res.status_code == 200
    history = res.json()["history"]
    assert len(history) >= 1
    assert history[0]["id"] == req_id

    # 5. Policies
    res = client.get("/api/approvals/policies")
    assert res.status_code == 200
    assert "policies" in res.json()

    res = client.post("/api/approvals/policies", json={"require_high_risk": True, "auto_approve_low_risk": True})
    assert res.status_code == 200
    assert res.json()["policies"]["require_high_risk"] is True


def test_graph_topology_and_simulation(client):
    # 1. Topology architecture
    res = client.get("/api/graph/topology")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert any(n["id"] == "quarantine_node" for n in data["nodes"])
    assert any(n["id"] == "approval_gate_node" for n in data["nodes"])

    # 2. Graph simulation
    res = client.post("/api/graph/simulate", json={"scenario": "rag", "prompt": "Explain architecture"})
    assert res.status_code == 200
    sim = res.json()
    assert sim["status"] == "success"
    assert "total_duration_ms" in sim
