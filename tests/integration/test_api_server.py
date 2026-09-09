"""Integration tests for the FastAPI Server and Command Center endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from server.app import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verify health endpoint returns status and model configs."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "config" in data


@pytest.mark.asyncio
async def test_inbox_ingest_and_retrieval_flow():
    """Verify inbound email ingestion, triage scoring, and inbox feed retrieval."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Ingest email
        payload = {
            "subject": "Interview Confirmation: AI Systems Engineer",
            "body": "Your interview is set for tomorrow at 3 PM on Google Meet.",
            "sender": "hiring@ai-corp.com",
            "is_known_contact": True,
        }
        ingest_res = await client.post("/api/inbox/ingest", json=payload)
        assert ingest_res.status_code == 200
        item = ingest_res.json()
        assert "id" in item
        assert "triage" in item
        assert item["triage"]["importance_score"] > 0.0

        # Retrieve inbox
        inbox_res = await client.get("/api/inbox")
        assert inbox_res.status_code == 200
        feed = inbox_res.json()["inbox"]
        assert len(feed) >= 1
        assert any(i["subject"] == payload["subject"] for i in feed)


@pytest.mark.asyncio
async def test_feedback_submission():
    """Verify user feedback increments the online streaming learner."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        feedback_payload = {
            "text": "Critical LangGraph checkpoint bug",
            "user_label": 1,
        }
        res = await client.post("/api/feedback", json=feedback_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "updated"
        assert "update_count" in data


@pytest.mark.asyncio
async def test_dashboard_html_render():
    """Verify dashboard UI loads properly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert "Sanctum" in res.text
        assert "Operations Overview" in res.text
