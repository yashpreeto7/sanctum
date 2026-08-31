"""Integration tests for MCP, Memory Graph, and Scheduler FastAPI Endpoints."""

import pytest
from fastapi.testclient import TestClient
from server.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_mcp_api_endpoints(client: TestClient):
    """Verify MCP servers and tools endpoints."""
    res = client.get("/api/mcp/servers")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "servers" in data
    assert isinstance(data["servers"], list)

    tools_res = client.get("/api/mcp/tools")
    assert tools_res.status_code == 200
    assert tools_res.json()["status"] == "success"


def test_memory_graph_api_endpoints(client: TestClient):
    """Verify Memory Graph CRUD endpoints."""
    # 1. Add Memory
    add_res = client.post("/api/memory/add", json={
        "entity": "test_bot",
        "attribute": "status",
        "value": "operational",
        "category": "system",
        "confidence": 1.0,
        "source": "api_test"
    })
    assert add_res.status_code == 200
    mem_id = add_res.json()["memory"]["id"]

    # 2. List Memories
    list_res = client.get("/api/memory/list")
    assert list_res.status_code == 200
    assert list_res.json()["count"] >= 1

    # 3. Search Memory
    search_res = client.get("/api/memory/search?q=operational")
    assert search_res.status_code == 200
    assert search_res.json()["count"] >= 1

    # 4. Delete Memory
    del_res = client.delete(f"/api/memory/{mem_id}")
    assert del_res.status_code == 200


def test_scheduler_api_endpoints(client: TestClient):
    """Verify Scheduler and Briefing endpoints."""
    status_res = client.get("/api/scheduler/status")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "success"

    briefing_res = client.get("/api/scheduler/briefing")
    assert briefing_res.status_code == 200
    assert "briefing" in briefing_res.json()
