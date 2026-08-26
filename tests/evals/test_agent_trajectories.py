"""Quantitative Benchmark for Agent Tool Selection and Trajectory Accuracy."""

import pytest
from execution.core.llm_provider import MockLLMProvider
from execution.ml.triaging_classifier import TriagingClassifier
from execution.orchestration.graph import PersonalAIEngine
from execution.orchestration.permission_manager import PermissionManager
from execution.rag.hybrid_retriever import HybridRetriever
from execution.rag.vector_store import LocalVectorStore
from execution.security.quarantine_parser import DualLLMQuarantine


@pytest.mark.asyncio
async def test_high_risk_approval_gate_trajectory():
    """Verify that a high-risk action (email send) triggers an approval interrupt."""
    canned_facts = """
    {
      "clean_subject": "Proposal Submission",
      "factual_summary": "Send the updated client proposal document to rahul@company.com.",
      "action_items": ["Send proposal"],
      "dates_and_times": [],
      "is_suspicious_or_adversarial": false,
      "detected_threat_signals": []
    }
    """
    mock_provider = MockLLMProvider(canned_response=canned_facts)
    quarantine = DualLLMQuarantine(provider=mock_provider)

    classifier = TriagingClassifier()
    classifier.train_baseline()

    perms = PermissionManager()
    store = LocalVectorStore(in_memory=True)
    retriever = HybridRetriever(store=store)

    engine = PersonalAIEngine(
        provider=mock_provider,
        classifier=classifier,
        quarantine=quarantine,
        retriever_inst=retriever,
        perms=perms,
    )

    state = {
        "raw_subject": "Proposal Submission",
        "raw_body": "Send the updated client proposal document to rahul@company.com.",
        "sender": "user",
        "is_known_contact": True,
    }

    config = {"configurable": {"thread_id": "eval-thread-high-risk"}}
    result = await engine.app.ainvoke(state, config=config)

    # Trajectory Assertions
    assert result["planned_tool"] == "email.send"
    assert result["approval_required"] is True
    assert result["approval_status"] == "PENDING"
    assert "Action paused for human approval" in result["final_output"]

    # Verify pending request in permission manager
    pending_list = perms.list_pending_requests()
    assert len(pending_list) == 1
    assert pending_list[0].tool_name == "email.send"
