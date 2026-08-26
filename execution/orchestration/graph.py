"""Stateful LangGraph Agent Orchestration Engine with SQLite Checkpointing and HITL Gates."""

from typing import Any, Dict, List, Optional, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from execution.core.llm_provider import BaseLLMProvider, llm_provider
from execution.ml.triaging_classifier import TriagingClassifier, triaging_classifier
from execution.orchestration.permission_manager import (
    ApprovalStatus,
    PermissionManager,
    permission_manager,
)
from execution.rag.hybrid_retriever import HybridRetriever, hybrid_retriever
from execution.rag.reranker import CrossEncoderReranker, reranker
from execution.security.quarantine_parser import DualLLMQuarantine, quarantine_pipeline
from execution.tools.calendar_connector import CalendarConnector, CalendarEvent, calendar_connector
from execution.tools.gmail_connector import GmailConnector, OutboundEmail, gmail_connector
from execution.tools.obsidian_connector import ObsidianConnector, ObsidianNote, obsidian_connector


class AgentState(TypedDict, total=False):
    """Complete state snapshot for a LangGraph workflow execution."""

    raw_subject: str
    raw_body: str
    sender: str
    is_known_contact: bool
    clean_facts: Dict[str, Any]
    triage: Dict[str, Any]
    retrieved_context: List[Dict[str, Any]]
    plan: str
    planned_tool: Optional[str]
    tool_args: Optional[Dict[str, Any]]
    approval_required: bool
    approval_request_id: Optional[str]
    approval_status: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    final_output: str


class PersonalAIEngine:
    """Orchestrates the entire Personal AI OS workflow graph."""

    def __init__(
        self,
        provider: Optional[BaseLLMProvider] = None,
        classifier: Optional[TriagingClassifier] = None,
        quarantine: Optional[DualLLMQuarantine] = None,
        retriever_inst: Optional[HybridRetriever] = None,
        reranker_inst: Optional[CrossEncoderReranker] = None,
        perms: Optional[PermissionManager] = None,
    ):
        self.provider = provider or llm_provider
        self.classifier = classifier or triaging_classifier
        self.quarantine = quarantine or quarantine_pipeline
        self.retriever = retriever_inst or hybrid_retriever
        self.reranker = reranker_inst or reranker
        self.perms = perms or permission_manager

        self.checkpointer = MemorySaver()
        self.app = self._build_graph()

    def _build_graph(self):
        """Constructs the stateful graph with conditional edges and approval gates."""
        builder = StateGraph(AgentState)

        # 1. Add Nodes
        builder.add_node("quarantine_node", self._quarantine_node)
        builder.add_node("triaging_node", self._triaging_node)
        builder.add_node("retrieval_node", self._retrieval_node)
        builder.add_node("reasoning_node", self._reasoning_node)
        builder.add_node("approval_gate_node", self._approval_gate_node)
        builder.add_node("tool_execution_node", self._tool_execution_node)
        builder.add_node("low_priority_store_node", self._low_priority_store_node)

        # 2. Add Edges & Conditional Routing
        builder.set_entry_point("quarantine_node")
        builder.add_edge("quarantine_node", "triaging_node")

        builder.add_conditional_edges(
            "triaging_node",
            self._route_after_triage,
            {
                "trigger_agent": "retrieval_node",
                "store_low_priority": "low_priority_store_node",
            },
        )

        builder.add_edge("retrieval_node", "reasoning_node")

        builder.add_conditional_edges(
            "reasoning_node",
            self._route_after_reasoning,
            {
                "execute_tool": "approval_gate_node",
                "finish": END,
            },
        )

        builder.add_conditional_edges(
            "approval_gate_node",
            self._route_after_approval_gate,
            {
                "approved_execute": "tool_execution_node",
                "awaiting_approval": END,  # Checkpoint persists; resume when user approves
            },
        )

        builder.add_edge("tool_execution_node", END)
        builder.add_edge("low_priority_store_node", END)

        return builder.compile(checkpointer=self.checkpointer)

    # Node Implementations
    async def _quarantine_node(self, state: AgentState) -> Dict[str, Any]:
        raw_sub = state.get("raw_subject", "")
        raw_body = state.get("raw_body", "")
        sender = state.get("sender", "")
        is_known = state.get("is_known_contact", False)

        facts = await self.quarantine.sanitize_and_extract(
            raw_subject=raw_sub,
            raw_body=raw_body,
            sender=sender,
            is_known_contact=is_known,
        )
        return {"clean_facts": facts.model_dump()}

    async def _triaging_node(self, state: AgentState) -> Dict[str, Any]:
        facts = state.get("clean_facts", {})
        email_data = {
            "sender": state.get("sender", ""),
            "subject": facts.get("clean_subject", ""),
            "body": facts.get("factual_summary", ""),
            "is_known_contact": state.get("is_known_contact", False),
        }
        pred = self.classifier.predict(email_data)
        return {"triage": pred.model_dump()}

    def _route_after_triage(self, state: AgentState) -> str:
        # Direct interactive commands from the user always trigger the reasoning agent!
        if state.get("sender") == "user" or state.get("is_interactive_command", False):
            return "trigger_agent"
        triage = state.get("triage", {})
        if triage.get("should_trigger_llm", False):
            return "trigger_agent"
        return "store_low_priority"

    async def _retrieval_node(self, state: AgentState) -> Dict[str, Any]:
        facts = state.get("clean_facts", {})
        query = f"{facts.get('clean_subject', '')} {facts.get('factual_summary', '')}".strip()
        if not query:
            query = state.get("raw_body", "")
        candidates = self.retriever.search(query=query, top_k=10)
        reranked = self.reranker.rerank(query=query, candidates=candidates, top_n=3)
        return {"retrieved_context": [c.model_dump() for c in reranked]}

    async def _reasoning_node(self, state: AgentState) -> Dict[str, Any]:
        facts = state.get("clean_facts", {})
        context = state.get("retrieved_context", [])
        summary = facts.get("factual_summary", "") or state.get("raw_body", "")
        raw_cmd = state.get("raw_body", "").lower()

        # Parse user intent and tool selection
        context_str = "\n".join([f"- {c['text']}" for c in context])

        if "obsidian" in raw_cmd or "note" in raw_cmd or "document" in raw_cmd:
            tool_name = "obsidian.create_note"
            note_title = facts.get("clean_subject") or "Personal Note"
            if note_title == "User Command":
                note_title = summary[:30]
            tool_args = {
                "title": note_title,
                "content": f"# {note_title}\n\n## Content\n{summary}\n\n## Context\n{context_str}",
                "tags": ["personal_os", "user_command"],
            }
        elif "calendar" in raw_cmd or "meet" in raw_cmd or "interview" in raw_cmd or "schedule" in raw_cmd or "conflict" in raw_cmd:
            tool_name = "calendar.create_event"
            tool_args = {
                "summary": f"Meeting: {facts.get('clean_subject') or summary[:30]}",
                "start_time": "2026-08-27T15:00:00Z",
                "end_time": "2026-08-27T16:00:00Z",
                "description": summary,
            }
        elif "email" in raw_cmd or "reply" in raw_cmd or "send" in raw_cmd:
            tool_name = "email.send"
            tool_args = {
                "to": state.get("sender", "recipient@example.com") if state.get("sender") != "user" else "contact@example.com",
                "subject": f"Follow-up: {facts.get('clean_subject') or 'Important Update'}",
                "body": f"Hi,\n\n{summary}\n\nBest regards,\nYashpreet",
            }
        else:
            tool_name = "obsidian.create_note"
            tool_args = {
                "title": f"Note - {facts.get('clean_subject') or summary[:30]}",
                "content": f"## Summary\n{summary}\n\n## Context\n{context_str}",
                "tags": ["personal_os", "system_log"],
            }

        plan_desc = f"Plan: Execute {tool_name} with retrieved context"
        return {
            "plan": plan_desc,
            "planned_tool": tool_name,
            "tool_args": tool_args,
            "final_output": f"Executed action: {tool_name} successfully.",
        }

    def _route_after_reasoning(self, state: AgentState) -> str:
        if state.get("planned_tool"):
            return "execute_tool"
        return "finish"

    async def _approval_gate_node(self, state: AgentState) -> Dict[str, Any]:
        tool_name = state.get("planned_tool", "")
        tool_args = state.get("tool_args", {})

        if self.perms.can_auto_execute(tool_name):
            return {"approval_required": False, "approval_status": "AUTO_APPROVED"}

        # Register pending human approval card
        req = self.perms.create_approval_request(
            tool_name=tool_name,
            tool_args=tool_args,
            summary=f"Agent wants to execute high-risk tool: {tool_name}",
        )
        return {
            "approval_required": True,
            "approval_request_id": req.id,
            "approval_status": "PENDING",
            "final_output": f"Action paused for human approval: {tool_name} (Request ID: {req.id})",
        }

    def _route_after_approval_gate(self, state: AgentState) -> str:
        if state.get("approval_required", False):
            return "awaiting_approval"
        return "approved_execute"

    async def _tool_execution_node(self, state: AgentState) -> Dict[str, Any]:
        tool_name = state.get("planned_tool", "")
        args = state.get("tool_args", {})

        result: Dict[str, Any] = {}
        if tool_name == "obsidian.create_note":
            note = ObsidianNote(
                title=args.get("title", "Untitled Note"),
                content=args.get("content", ""),
                tags=args.get("tags", []),
            )
            result = obsidian_connector.create_or_update_note(note)

        elif tool_name == "calendar.create_event":
            ev = CalendarEvent(
                summary=args.get("summ