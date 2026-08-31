"""Quantitative Benchmark for Agent Tool Selection and Trajectory Accuracy."""

import pytest
from execution.core.llm_provider import MockLLMProvider
from execution.ml.triaging_classifier import TriagingClassifier
from execution.orchestration.graph import PersonalAIEngine
from execution.orchestration.permission_manager import PermissionManager
from execution.rag.hybrid_retriever import HybridRetriever
from execution.rag.vector_store import LocalVectorStore
from execution.security.quarantine_parser import DualLLMQuarantine


@pytest.fixture
def test_engine():
    canned_facts = """
    {
      "clean_subject": "User Request",
      "factual_summary": "Process user request.",
      "action_items": [],
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
    return PersonalAIEngine(
        provider=mock_provider,
        classifier=classifier,
        quarantine=quarantine,
        retriever_inst=retriever,
        perms=perms,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,expected_tool,expected_arg_key,expected_arg_val",
    [
        # Inbound Search / Checking (Must NEVER trigger email.send)
        ("check if i recieved any email from jashanjashan372@gmail.com", "email.search", "query", "jashanjashan372@gmail.com"),
        ("check if i received email from test@domain.com", "email.search", "query", "test@domain.com"),
        ("did i get any emails from rahul", "email.search", "query", "rahul"),
        ("show me email from linkedin", "email.search", "query", "linkedin"),
        ("search emails for invoice", "email.search", "query", "invoice"),
        ("have i received any email from sarah", "email.search", "query", "sarah"),
        
        # Ordinal Lookups
        ("read the first email", "email.get_email", "identifier", "first"),
        ("open the 2nd email", "email.get_email", "identifier", "2"),
        ("show email #3", "email.get_email", "identifier", "3"),
        
        # Unread List
        ("show my unread emails", "email.list_unread", "query", "is:unread"),
        ("check inbox", "email.list_unread", "query", "is:unread"),
        
        # Outbound Send (Explicit Sending Action)
        ("send a mail to jashanjashan372@gmail.com saying its a test mail and add other content", "email.send", "to", "jashanjashan372@gmail.com"),
        ("email rahul saying project update is ready", "email.send", "to", "rahul@techcorp.io"),
        ("send an email to contact@company.org", "email.send", "to", "contact@company.org"),
        
        # Calendar
        ("what meetings do i have", "calendar.list_events", "query", "upcoming"),
        ("schedule a meeting tomorrow at 3pm", "calendar.create_event", "summary", "Meeting:"),
        
        # Notes
        ("save note about project roadmap", "obsidian.create_note", "title", "roadmap"),
        ("search notes for architecture design", "obsidian.search_notes", "query", "architecture design"),
    ],
)
async def test_agent_intent_trajectory_classification(test_engine, query, expected_tool, expected_arg_key, expected_arg_val):
    """Verify high-precision tool routing and argument extraction across all natural language variations."""
    state = {
        "raw_subject": "User Command",
        "raw_body": query,
        "sender": "user",
        "is_known_contact": True,
        "is_interactive_command": True,
    }
    result = await test_engine.app.ainvoke(state, config={"configurable": {"thread_id": f"eval-{hash(query)}"}})
    assert result["planned_tool"] == expected_tool, f"Query '{query}' expected '{expected_tool}' but got '{result.get('planned_tool')}'"
    assert expected_arg_key in result["tool_args"], f"Expected argument key '{expected_arg_key}' in {result['tool_args']}"
    if expected_arg_val:
        assert expected_arg_val in str(result["tool_args"][expected_arg_key]), f"Expected '{expected_arg_val}' in {result['tool_args'][expected_arg_key]}"
