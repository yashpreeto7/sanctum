"""
Unit tests for DeepResearcher in Personal AI OS.
"""
from pathlib import Path
import pytest
from execution.tools.deep_researcher import DeepResearcher


@pytest.fixture
def researcher(tmp_path: Path):
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    return DeepResearcher(vault_dir=vault_dir)


def test_decompose_topic(researcher: DeepResearcher):
    topic = "vLLM PagedAttention vs SGLang RadixAttention"
    sub_inquiries = researcher.decompose_topic(topic)
    assert len(sub_inquiries) == 4
    aspects = [item["aspect"] for item in sub_inquiries]
    assert "Architecture & Core Concepts" in aspects
    assert "Benchmarks & Trade-offs" in aspects


def test_generate_mermaid_diagram(researcher: DeepResearcher):
    # 1. Comparative diagram
    diag_comp = researcher.generate_mermaid_diagram("vLLM vs SGLang", [])
    assert "Comparative Architecture" in diag_comp
    assert "Engine A Pipeline" in diag_comp

    # 2. RAG diagram
    diag_rag = researcher.generate_mermaid_diagram("Hybrid RAG Vector Pipeline", [])
    assert "Hybrid Retrieval" in diag_rag
    assert "Cross-Encoder Reranker" in diag_rag


def test_conduct_research_and_obsidian_export(researcher: DeepResearcher, monkeypatch):
    # Mock search_web to prevent network calls in unit tests
    def mock_search_web(query: str, max_results: int = 5):
        return [
            {
                "title": f"Documentation for {query[:20]}",
                "snippet": f"This is an architectural summary for {query[:30]} with high performance benchmarks.",
                "url": "https://example.com/docs/arch"
            }
        ]

    monkeypatch.setattr("execution.tools.deep_researcher.search_web", mock_search_web)

    dossier = researcher.conduct_research("vLLM PagedAttention Architecture", depth=2)
    assert dossier["topic"] == "vLLM PagedAttention Architecture"
    assert len(dossier["sections"]) == 4
    assert len(dossier["sources"]) >= 1
    assert "mermaid_diagram" in dossier

    # Check Obsidian note creation
    research_dir = researcher.vault_dir / "Research"
    assert research_dir.exists()
    note_files = list(research_dir.glob("*.md"))
    assert len(note_files) == 1
    content = note_files[0].read_text(encoding="utf-8")
    assert "Deep Research Dossier: vLLM PagedAttention Architecture" in content
    assert "```mermaid" in content
