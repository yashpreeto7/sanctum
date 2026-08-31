"""Unit tests for Persistent Episodic & Semantic Memory Graph (Mem0-Style)."""

import pytest
from pathlib import Path
from execution.ml.memory_graph import MemoryGraph


@pytest.fixture
def temp_memory_graph(tmp_path: Path):
    db_file = tmp_path / "test_memory.sqlite"
    return MemoryGraph(db_path=db_file)


def test_memory_graph_seed_and_count(temp_memory_graph: MemoryGraph):
    """Verify seed default memories are populated on fresh database."""
    count = temp_memory_graph.count_memories()
    assert count >= 5
    mems = temp_memory_graph.get_all_memories()
    assert any(m["entity"] == "user" and m["attribute"] == "name" for m in mems)


def test_memory_graph_add_update_delete(temp_memory_graph: MemoryGraph):
    """Verify CRUD lifecycle of facts."""
    mem = temp_memory_graph.add_or_update_memory(
        entity="user",
        attribute="favorite_framework",
        value="FastAPI + LangGraph",
        category="preference",
        confidence=0.95,
        source="unit_test"
    )
    assert mem["entity"] == "user"
    assert mem["attribute"] == "favorite_framework"
    assert mem["value"] == "FastAPI + LangGraph"
    mem_id = mem["id"]

    # Search
    search_res = temp_memory_graph.search_memories("FastAPI")
    assert len(search_res) >= 1
    assert search_res[0]["value"] == "FastAPI + LangGraph"

    # Context formatting
    ctx = temp_memory_graph.get_context_for_prompt("FastAPI")
    assert "<persistent_memory_context>" in ctx
    assert "FastAPI + LangGraph" in ctx

    # Delete
    deleted = temp_memory_graph.delete_memory(mem_id)
    assert deleted is True

    # Search should no longer return it
    search_after = temp_memory_graph.search_memories("FastAPI")
    assert not any(m["id"] == mem_id for m in search_after)


def test_memory_graph_heuristic_extraction(temp_memory_graph: MemoryGraph):
    """Verify pattern matching extracts preferences from text."""
    text = "I prefer dark mode with high contrast and my project is called Sovereign Engine"
    extracted = temp_memory_graph.extract_memories_from_text(text, source="chat")
    assert len(extracted) >= 1
    attrs = [e["attribute"] for e in extracted]
    assert "preference" in attrs or "active_project" in attrs
