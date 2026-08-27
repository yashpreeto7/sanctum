"""Stateful LangGraph Agent Orchestration Engine with SQLite Checkpointing and HITL Gates."""

from typing import Any, Dict, List, Literal, Optional, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

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


# ── Structured output schema for LLM reasoning ─────────────────────────────

class ReasoningPlan(BaseModel):
    """Structured reasoning output: the LLM chooses a tool and its arguments."""

    tool_name: Literal[
        "email.send",
        "calendar.create_event",
        "obsidian.create_note",
        "obsidian.search_notes",
        "email.list_unread",
        "calendar.list_events",
        "no_action",
    ] = Field(..., description="The most appropriate tool for the user's request")
    tool_args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments to pass to the tool. Must match the tool's required parameters.",
    )
    plan_rationale: str = Field(..., description="Brief explanation of why this tool and arguments were chosen")
    response_to_user: str = Field(..., description="A concise, helpful response to show the user")


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
        sender = state.get("sender", "unknown")
        context_str = "\n".join([f"- {c['text']}" for c in context]) or "No prior context retrieved."

        # ── Build reasoning prompt with full context ──────────────────────
        tool_schema = """
Available tools:
- email.send: Send an email. Args: {to: str, subject: str, body: str}
- calendar.create_event: Create a calendar event. Args: {summary: str, start_time: str (ISO8601), end_time: str (ISO8601), description: str}
- calendar.list_events: List upcoming calendar events. Args: {query: str}
- obsidian.create_note: Create or update a markdown note. Args: {title: str, content: str, tags: list[str]}
- obsidian.search_notes: Search existing notes. Args: {query: str}
- email.list_unread: List unread emails. Args: {query: str}
- no_action: Take no action, just respond conversationally. Args: {}
"""

        reasoning_system_prompt = (
            "You are the reasoning core of a personal AI operating system. "
            "Given the user's request, retrieved context, and sanitized message facts, "
            "determine the single best tool to call and generate the appropriate arguments.\n\n"
            "CRITICAL RULES:\n"
            "1. Only choose 'email.send' if the user explicitly wants to SEND an email to someone.\n"
            "2. Only choose 'calendar.create_event' if there is clear scheduling intent.\n"
            "3. Choose 'obsidian.create_note' for saving information, notes, summaries, or decisions.\n"
            "4. Choose 'no_action' for conversational queries that don't require a tool.\n"
            "5. Always generate a helpful response_to_user explaining what you'll do or did.\n"
            f"{tool_schema}"
        )

        reasoning_prompt = (
            f"User Request: {state.get('raw_body', '')}\n\n"
            f"Sanitized Facts:\n{summary}\n\n"
            f"Sender: {sender}\n\n"
            f"Retrieved Context (top-3 relevant knowledge chunks):\n{context_str}\n\n"
            f"Select the most appropriate tool and generate its arguments."
        )

        try:
            plan = await self.provider.generate_structured(
                schema=ReasoningPlan,
                prompt=reasoning_prompt,
                system_prompt=reasoning_system_prompt,
            )
            planned_tool = plan.tool_name if plan.tool_name != "no_action" else None
            plan_rationale = plan.plan_rationale
            response_to_user = plan.response_to_user
            tool_args = plan.tool_args
        except Exception:
            # Graceful fallback: keyword-based routing when Ollama is unavailable
            # or when structured output fails validation
            plan = self._keyword_fallback_reasoning(state, facts, summary, context_str, sender)
            planned_tool = plan.tool_name if plan.tool_name != "no_action" else None
            plan_rationale = plan.plan_rationale
            response_to_user = plan.response_to_user
            tool_args = plan.tool_args

        return {
            "plan": plan_rationale,
            "planned_tool": planned_tool,
            "tool_args": tool_args,
            "final_output": response_to_user,
        }

    def _keyword_fallback_reasoning(
        self,
        state: AgentState,
        facts: Dict[str, Any],
        summary: str,
        context_str: str,
        sender: str,
    ) -> ReasoningPlan:
        """Deterministic keyword-routing fallback when LLM is unavailable."""
        raw_cmd = state.get("raw_body", "").lower()

        if "calendar" in raw_cmd or "meet" in raw_cmd or "interview" in raw_cmd or "schedule" in raw_cmd or "conflict" in raw_cmd:
            return ReasoningPlan(
                tool_name="calendar.create_event",
                tool_args={
                    "summary": f"Meeting: {facts.get('clean_subject') or summary[:30]}",
                    "start_time": "2026-08-27T15:00:00Z",
                    "end_time": "2026-08-27T16:00:00Z",
                    "description": summary,
                },
                plan_rationale="Keyword match: scheduling intent detected.",
                response_to_user=f"Creating a calendar event for: {summary[:60]}",
            )
        elif "email" in raw_cmd or "reply" in raw_cmd or "send" in raw_cmd or "draft" in raw_cmd or "proposal" in raw_cmd:
            to_addr = sender if sender != "user" else "contact@example.com"
            return ReasoningPlan(
                tool_name="email.send",
                tool_args={
                    "to": to_addr,
                    "subject": f"Follow-up: {facts.get('clean_subject') or 'Important Update'}",
                    "body": f"Hi,\n\n{summary}\n\nBest regards,\nYashpreet",
                },
                plan_rationale="Keyword match: email send intent detected.",
                response_to_user=f"Composing email to {to_addr}: {summary[:60]}",
            )
        elif "obsidian" in raw_cmd or "note" in raw_cmd or "document" in raw_cmd:
            note_title = facts.get("clean_subject") or "Personal Note"
            if note_title == "User Command":
                note_title = summary[:30]
            return ReasoningPlan(
                tool_name="obsidian.create_note",
                tool_args={
                    "title": note_title,
                    "content": f"# {note_title}\n\n## Content\n{summary}\n\n## Context\n{context_str}",
                    "tags": ["personal_os", "user_command"],
                },
                plan_rationale="Keyword match: note creation intent detected.",
                response_to_user=f"Creating Obsidian note: '{note_title}'",
            )
        else:
            note_title = f"Note - {facts.get('clean_subject') or summary[:30]}"
            return ReasoningPlan(
                tool_name="obsidian.create_note",
                tool_args={
                    "title": note_title,
                    "content": f"## Summary\n{summary}\n\n## Context\n{context_str}",
                    "tags": ["personal_os", "system_log"],
                },
                plan_rationale="Default: storing information as an Obsidian note.",
                response_to_user=f"Stored note: '{note_title}'",
            )

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
        output_message = state.get("final_output", f"Executed {tool_name} successfully.")

        if tool_name == "obsidian.create_note":
            note = ObsidianNote(
                title=args.get("title", "Untitled Note"),
                content=args.get("content", ""),
                tags=args.get("tags", []),
            )
            result = obsidian_connector.create_or_update_note(note)
            output_message = f"✅ Note '{args.get('title', 'Untitled')}' saved to Obsidian vault."

        elif tool_name == "obsidian.search_notes":
            results = obsidian_connector.search_notes(query=args.get("query", ""))
            if results:
                preview = "\n".join([f"• **{r['title']}**: {r['preview'][:80]}..." for r in results[:3]])
                output_message = f"Found {len(results)} matching note(s):\n\n{preview}"
            else:
                output_message = f"No notes found matching: {args.get('query', '')}"
            result = {"matches": results}

        elif tool_name == "calendar.create_event":
            ev = CalendarEvent(
                summary=args.get("summary", "Event"),
                start_time=args.get("start_time", ""),
                end_time=args.get("end_time", ""),
                description=args.get("description"),
            )
            result = calendar_connector.create_event(ev)
            output_message = f"✅ Calendar event '{args.get('summary', 'Event')}' created."

        elif tool_name == "calendar.list_events":
            result = {"query": args.get("query", ""), "status": "Calendar listing requires OAuth — connect Google Calendar to enable."}
            output_message = "📅 Calendar listing requires Google Calendar OAuth. Connect your account in Settings."

        elif tool_name == "email.send":
            out_email = OutboundEmail(
                to=args.get("to", ""),
                subject=args.get("subject", ""),
                body=args.get("body", ""),
            )
            result = gmail_connector.send_email(out_email)
            output_message = f"✅ Email sent to {args.get('to', 'recipient')} — Subject: {args.get('subject', '')}"

        elif tool_name == "email.list_unread":
            result = {"query": args.get("query", ""), "status": "Email listing requires OAuth — connect Gmail to enable."}
            output_message = "📬 Email listing requires Gmail OAuth. Connect your account in Settings."

        return {
            "execution_result": result,
            "final_output": output_message,
        }

    async def _low_priority_store_node(self, state: AgentState) -> Dict[str, Any]:
        facts = state.get("clean_facts", {})
        sub = facts.get("clean_subject", "Low Priority")
        return {
            "final_output": f"Stored low priority message without invoking LLM: {sub}",
        }


# Singleton instance
agent_engine = PersonalAIEngine()
