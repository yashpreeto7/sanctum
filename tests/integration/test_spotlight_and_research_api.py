"""
Integration tests for Spotlight HUD, Deep Research, and Universal Document API endpoints.
"""
from fastapi.testclient import TestClient
import pytest
from server.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_spotlight_search_endpoint(client: TestClient):
    # Search for quick actions
    resp = client.get("/api/spotlight/search?q=research")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert "actions" in data["results"]
    assert any("Research" in a["title"] for a in data["results"]["actions"])


def test_deep_research_endpoint(client: TestClient, monkeypatch):
    def mock_search_web(query: str, max_results: int = 5):
        return [
            {
                "title": "vLLM High-Throughput LLM Serving",
                "snippet": "vLLM utilizes PagedAttention to eliminate memory fragmentation.",
                "url": "https://vllm.ai"
            }
        ]

    monkeypatch.setattr("execution.tools.deep_researcher.search_web", mock_search_web)

    resp = client.post("/api/research/run", json={"topic": "vLLM PagedAttention", "depth": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "dossier" in data
    assert data["dossier"]["topic"] == "vLLM PagedAttention"
    assert "mermaid_diagram" in data["dossier"]

    # Test history endpoint
    hist_resp = client.get("/api/research/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert "history" in hist_data
    if hist_data["history"]:
        sample_file = hist_data["history"][0]["filename"]
        dossier_resp = client.get(f"/api/research/dossier?filename={sample_file}")
        assert dossier_resp.status_code == 200
        dossier_data = dossier_resp.json()
        assert "content" in dossier_data
        assert len(dossier_data["content"]) > 0


def test_document_upload_and_list_endpoint(client: TestClient):
    file_content = b"# Architecture Decision Record\n\nADR-001: Use Qdrant for Hybrid Vector Indexing."
    files = {"file": ("adr_001.md", file_content, "text/markdown")}

    upload_resp = client.post("/api/documents/upload", files=files)
    assert upload_resp.status_code == 200
    data = upload_resp.json()
    assert data["status"] == "success"
    assert data["document"]["filename"] == "adr_001.md"

    # Test list documents
    list_resp = client.get("/api/documents")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert "documents" in list_data
    assert any(d["filename"] == "adr_001.md" for d in list_data["documents"])

    # Test sync documents
    sync_resp = client.post("/api/documents/sync")
    assert sync_resp.status_code == 200
