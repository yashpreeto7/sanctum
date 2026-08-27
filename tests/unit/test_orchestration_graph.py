"""Unit tests for the LangGraph Orchestration Engine and Permission Manager."""

import pytest
from execution.core.llm_provider import MockLLMProvider
from execution.ml.triaging_classifier import TriagingClassifier
from execution.orchestration.graph import PersonalAIEngine
from execution.orchestration.permission_manager import ApprovalStatus, PermissionManager
from execution.rag.hybrid_retriever import HybridRetriever
from execution.rag.vector_store import LocalVectorStore
from execution.security.quarantine_parser import DualLLMQuarantine


@pytest.fixture
def mock_engine():
    """Provides a fully wired in-memory PersonalAIEngine for unit testing."""
    canned_facts = """
    {
      "clean_subject": "Staging server incident",
      "factual_summary": "Rahul sent a message asking to sync on the staging API outage.",
      "action_items": ["Sync with team"],
      "dates_and_times": [],
      "is_suspicious_or_adversarial": false,
      "detected_threat_signals": []
    }
    """
    mock_provider = MockLLMProvider(canned_response=canned_facts)
    quarantine = DualLLMQuarantine(provider=mock_provider)

    classifier = TriagingClassifier()
    classifier.train_baseline()

    store = LocalVectorStore(in_memory=True)
    retriever = HybridRetriever(store=store)
    perms = PermissionManager()

    engine = PersonalAIEngine(
        provider=mock_provider,
        classifier=classifier,
        quarantine=quarantine,
        retriever_inst=retriever,
        perms=perms,
    )
    return engine


@pytest.mark.asyncio
async def test_graph_low_priority_bypass(mock_engine):
    """Verify newsletter/promotional email bypasses the heavy agent and stores directly."""
    canned_promo = """
    {
      "clean_subject": "50% OFF Newsletter",
      "factual_summary": "Weekly shopping discount digest.",
      "action_items": [],
      "dates_and_times": [],
      "is_suspicious_or_adversarial": false,
      "detected_threat_signals": []
    }
    """
    mock_engine.quarantine.provider = MockLLMProvider(canned_response=canned_promo)

    initial_state = {
        "raw_subject": "50% OFF Newsletter",
        "raw_body": "Weekly shopping discount digest. Unsubscribe here.",
        "sender": "news@store.com",
        "is_known_contact": False,
    }

    config = {"configurable": {"thread_id": "test-thread-1"}}
    result = await mock_engine.app.ainvoke(initial_state, config=config)

    assert result["triage"]["predicted_category"] in ["newsletter_promo", "marketing_promo"]
    assert "Stored low priority message" in result["final_output"]


@pytest.mark.asyncio
async def test_graph_important_email_auto_note(mock_engine):
    """Verify important message triggers retrieval and creates an Obsidian note."""
    initial_state = {
        "raw_subject": "URGENT: Staging API Gateway Outage",
        "raw_body": "Please review the doc and sync ASAP.",
        "sender": "rahul@company.com",
        "is_known_contact": True,
    }

    config = {"configurable": {"thread_id": "test-thread-2"}}
    result = await mock_engine.app.ainvoke(initial_state, config=config)

    assert result["triage"]["should_trigger_llm"] is True
    assert result["planned_tool"] == "obsidian.create_note"
    assert result["execution_result"]["status"] == "success"


def test_permission_manager_queue_and_resolution():
    """Verify permission manager creates approval requests and resolves them."""
    perms = PermissionManager()

    req = perms.create_approval_request(
        tool_name="email.send",
        tool_args={"to": "client@acme.com", "subject": "Proposal"},
        summary="Send proposal to client",
    )
    assert req.risk_level == "HIGH"
    assert req.status == ApprovalStatus.PENDING

    # Resolve approval
    resolved = perms.resolve_request(req.id, approved=True)
    assert resolved.status == ApprovalStatus.APPROVED
    assert len(perms.list_pending_requests()) == 0
