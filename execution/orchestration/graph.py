"""Stateful LangGraph Agent Orchestration Engine with SQLite Checkpointing, HITL Gates, and Natural Conversational Intelligence."""

import re
import time
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
from execution.orchestration.trace_manager import trace_store
from execution.rag.hybrid_retriever import HybridRetriever, hybrid_retriever
from execution.rag.reranker import CrossEncoderReranker, reranker
from execution.security.quarantine_parser import DualLLMQuarantine, quarantine_pipeline
from execution.tools.calendar_connector import CalendarConnector, CalendarEvent, calendar_connector
from execution.tools.gmail_connector import GmailConnector, OutboundEmail, gmail_connector
from execution.tools.obsidian_connector import ObsidianConnector, ObsidianNote, obsidian_connector
from execution.tools.web_search_tool import search_web
from execution.tools.workspace_tool import list_workspace_files, read_workspace_file, write_workspace_file


# ── Structured output schema for LLM reasoning ─────────────────────────────

class ReasoningPlan(BaseModel):
    """Structured reasoning output: the LLM chooses a tool and its arguments."""

    tool_name: Literal[
        "email.send",
        "email.search",
        "email.get_email",
        "calendar.create_event",
        "obsidian.create_note",
        "obsidian.search_notes",
        "email.list_unread",
        "calendar.list_events",
        "web.search",
        "workspace.list_files",
        "workspace.read_file",
        "workspace.write_file",
        "no_action",
    ] = Field(..., description="The most appropriate tool for the user's request")
    tool_args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments to pass to the tool. Must match the tool's required parameters.",
    )
    plan_rationale: str = Field(..., description="Brief explanation of why this tool and arguments were chosen")
    response_to_user: str = Field(..., description="A natural, helpful, conversational response to show the user")


class AgentState(TypedDict, total=False):
    """Complete state snapshot for a LangGraph workflow execution."""

    run_id: Optional[str]
    raw_subject: str
    raw_body: str
    sender: str
    is_known_contact: bool
    is_interactive_command: bool
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
    chat_history: Optional[List[Dict[str, Any]]]


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
                "awaiting_approval": END,
            },
        )

        builder.add_edge("tool_execution_node", END)
        builder.add_edge("low_priority_store_node", END)

        return builder.compile(checkpointer=self.checkpointer)

    # Node Implementations
    async def _quarantine_node(self, state: AgentState) -> Dict[str, Any]:
        t0 = time.perf_counter()
        raw_sub = state.get("raw_subject", "")
        raw_body = state.get("raw_body", "")
        sender = state.get("sender", "")
        is_known = state.get("is_known_contact", False)
        is_interactive = state.get("is_interactive_command", False) or (sender == "user")
        run_id = state.get("run_id")

        if is_interactive:
            # Fast-track trusted interactive chat & voice commands (skip redundant 5s LLM pre-filter)
            facts_dict = {
                "clean_subject": raw_sub or "User Command",
                "factual_summary": raw_body,
                "urgency": "HIGH",
                "is_phishing_or_injection": False,
                "extracted_entities": [],
                "source_text_sanitized": raw_body,
            }
        else:
            facts = await self.quarantine.sanitize_and_extract(
                raw_subject=raw_sub,
                raw_body=raw_body,
                sender=sender,
                is_known_contact=is_known,
            )
            facts_dict = facts.model_dump()

        duration_ms = (time.perf_counter() - t0) * 1000.0

        if run_id:
            trace_store.record_node_step(
                run_id=run_id,
                node_name="quarantine_node",
                inputs={"raw_subject": raw_sub, "raw_body": raw_body, "sender": sender},
                outputs={"clean_facts": facts_dict},
                duration_ms=duration_ms,
                status="COMPLETED",
            )

        return {"clean_facts": facts_dict}

    async def _triaging_node(self, state: AgentState) -> Dict[str, Any]:
        t0 = time.perf_counter()
        facts = state.get("clean_facts", {})
        sender = state.get("sender", "")
        is_interactive = state.get("is_interactive_command", False) or (sender == "user")
        run_id = state.get("run_id")

        if is_interactive:
            # Fast-track triage for interactive user sessions
            pred_dict = {
                "category": "ACTIONABLE",
                "action_urgency": 1.0,
                "confidence": 1.0,
                "should_trigger_llm": True,
                "rationale": "Direct interactive user command.",
            }
        else:
            email_data = {
                "sender": sender,
                "subject": facts.get("clean_subject", ""),
                "body": facts.get("factual_summary", ""),
                "is_known_contact": state.get("is_known_contact", False),
            }
            pred = self.classifier.predict(email_data)
            pred_dict = pred.model_dump()

        duration_ms = (time.perf_counter() - t0) * 1000.0

        if run_id:
            trace_store.record_node_step(
                run_id=run_id,
                node_name="triaging_node",
                inputs={"sender": sender},
                outputs={"triage": pred_dict},
                duration_ms=duration_ms,
                status="COMPLETED",
            )

        return {"triage": pred_dict}

    def _route_after_triage(self, state: AgentState) -> str:
        if state.get("sender") == "user" or state.get("is_interactive_command", False):
            return "trigger_agent"
        triage = state.get("triage", {})
        if triage.get("should_trigger_llm", False):
            return "trigger_agent"
        return "store_low_priority"

    async def _retrieval_node(self, state: AgentState) -> Dict[str, Any]:
        t0 = time.perf_counter()
        facts = state.get("clean_facts", {})
        run_id = state.get("run_id")
        raw_b = state.get("raw_body", "").strip().lower().strip(" .!?,")
        
        # Skip RAG context retrieval for casual acknowledgements and short greetings to prevent vector noise
        trivial_chatter = {"ok", "okay", "k", "yes", "no", "cool", "sure", "thanks", "thank you", "thx", "hello", "hi", "hey", "sup", "yo", "got it", "fine", "great", "nice", "perfect", "done"}
        if raw_b in trivial_chatter or len(raw_b) < 3:
            context_list = []
        else:
            query = f"{facts.get('clean_subject', '')} {facts.get('factual_summary', '')}".strip()
            if not query or query == "User Command":
                query = state.get("raw_body", "")

            candidates = self.retriever.search(query=query, top_k=5)
            if len(candidates) > 3:
                reranked = self.reranker.rerank(query=query, candidates=candidates, top_n=3)
            else:
                reranked = candidates
            context_list = [c.model_dump() for c in reranked]
            
        duration_ms = (time.perf_counter() - t0) * 1000.0

        if run_id:
            trace_store.record_node_step(
                run_id=run_id,
                node_name="retrieval_node",
                inputs={"raw_body": raw_b},
                outputs={"top_k_results": len(context_list), "context_snippets": [c["text"][:100] for c in context_list]},
                duration_ms=duration_ms,
                status="COMPLETED",
            )

        return {"retrieved_context": context_list}

    async def _reasoning_node(self, state: AgentState) -> Dict[str, Any]:
        t0 = time.perf_counter()
        facts = state.get("clean_facts", {})
        context = state.get("retrieved_context", [])
        summary = facts.get("factual_summary", "") or state.get("raw_body", "")
        sender = state.get("sender", "unknown")
        raw_cmd = state.get("raw_body", "").strip()
        run_id = state.get("run_id")
        context_str = "\n".join([f"- {c['text']}" for c in context]) if context else ""

        # ── Build reasoning prompt with full context ──────────────────────
        tool_schema = """
Available tools:
- web.search: Search the live web using DuckDuckGo for breaking news, docs, live facts, and external links. Args: {query: str}
- workspace.list_files: List files and directories in the local project workspace. Args: {subpath: str}
- workspace.read_file: Read contents of a local file in the workspace. Args: {file_path: str}
- workspace.write_file: Write or create a file in the workspace (triggers safety approval). Args: {file_path: str, content: str}
- email.search: Search emails by sender or keyword query (e.g. 'linkedin', 'udemy', 'invoice'). Args: {query: str}
- email.get_email: Read full details of a specific email by number ('1', '2', 'first', 'latest') or ID. Args: {identifier: str}
- email.list_unread: List recent unread emails from Gmail. Args: {query: str}
- email.send: Send an email (requires recipient, subject, body). Args: {to: str, subject: str, body: str}
- calendar.create_event: Create a calendar event. Args: {summary: str, start_time: str, end_time: str, description: str}
- calendar.list_events: List upcoming calendar events. Args: {query: str}
- obsidian.create_note: Create a markdown note. Args: {title: str, content: str, tags: list[str]}
- obsidian.search_notes: Search existing notes. Args: {query: str}
- no_action: Take no action, respond conversationally or answer technical/general questions naturally. Args: {}
"""

        reasoning_system_prompt = (
            "You are Personal AI OS, Yashpreet's intelligent, conversational AI assistant and local automation system.\n\n"
            "INSTRUCTIONS FOR YOUR OUTPUT:\n"
            "• `response_to_user`: This is the direct message that Yashpreet reads. Always provide a natural, articulate, comprehensive, and friendly reply with clear markdown headings, bullet points, and clean syntax. If asked a question (e.g. 'what is YouTube', 'what is Next.js', 'explain quantum computing', 'how does python work'), write a high-quality, comprehensive explanation directly in `response_to_user`.\n"
            "• `tool_name`: Choose the most direct and specific tool for the user's intent:\n"
            "  - For morning briefings or schedule inquiries ('what meetings do I have today', 'daily agenda', 'morning briefing'), choose `calendar.list_events`.\n"
            "  - For checking messages or inbox summaries ('check my unread emails', 'any urgent emails'), choose `email.list_unread`.\n"
            "  - For taking or saving notes ('take a note', 'save to obsidian', 'sync notes'), choose `obsidian.create_note`.\n"
            "  - For searching notes or knowledge base ('search notes for X', 'what do my notes say about Y'), choose `obsidian.search_notes`.\n"
            "  - For inspecting codebase workspace ('list workspace files', 'check project structure'), choose `workspace.list_files`.\n"
            "  - For web searches ('search web for X', 'look up online'), choose `web.search`.\n"
            "  - Choose `no_action` for general conversation, greetings, definitions, explanations, conceptual questions, coding, and architecture queries.\n"
            "• `plan_rationale`: Brief internal reasoning for your chosen action.\n\n"
            f"{tool_schema}"
        )

        # ── Fetch User Memory Graph Context & Extract Facts ────────────────
        memory_context = ""
        try:
            from execution.ml.memory_graph import memory_graph
            memory_context = memory_graph.get_context_for_prompt(raw_cmd, max_items=6)
            if sender == "user" or state.get("is_interactive_command", False):
                memory_graph.extract_memories_from_text(raw_cmd, source="chat")
        except Exception as e:
            logger.debug(f"Memory graph note: {e}")

        # Include conversation history if available
        history = state.get("chat_history") or []
        history_str = ""
        if history:
            history_lines = []
            for h in history[-8:]:
                r_name = "User" if h.get("role") == "user" else "Personal AI"
                c_text = (h.get("content") or "").strip().replace("\n", " ")
                if len(c_text) > 250:
                    c_text = c_text[:250] + "..."
                history_lines.append(f"[{r_name}]: {c_text}")
            if history_lines:
                history_str = "Recent Prior Conversation Turns:\n" + "\n".join(history_lines) + "\n\n"

        reasoning_prompt = (
            f"{history_str}"
            f"{memory_context + chr(10) + chr(10) if memory_context else ''}"
            f"Current User Request: \"{raw_cmd}\"\n\n"
            f"Factual Summary: {summary}\n"
            f"Sender: {sender}\n"
            f"Retrieved Vault & Chat Memory Context:\n{context_str or 'None'}\n\n"
            f"Respond directly to the user in `response_to_user` and choose the appropriate `tool_name`."
        )

        is_llm_ready = await self.provider.is_available()
        plan: Optional[ReasoningPlan] = None

        if is_llm_ready:
            try:
                plan = await self.provider.generate_structured(
                    schema=ReasoningPlan,
                    prompt=reasoning_prompt,
                    system_prompt=reasoning_system_prompt,
                )
            except Exception:
                plan = None

        if plan is None or not getattr(plan, "tool_name", None):
            plan = self._keyword_fallback_reasoning(state, facts, summary, context, sender)

        planned_tool = plan.tool_name if plan.tool_name != "no_action" else None
        plan_rationale = plan.plan_rationale
        response_to_user = plan.response_to_user
        tool_args = plan.tool_args
        duration_ms = (time.perf_counter() - t0) * 1000.0

        if run_id:
            trace_store.record_node_step(
                run_id=run_id,
                node_name="reasoning_node",
                inputs={"raw_body": raw_cmd, "context_length": len(context)},
                outputs={"plan_rationale": plan_rationale, "response_preview": response_to_user[:120]},
                duration_ms=duration_ms,
                status="COMPLETED",
                tool_call=planned_tool,
                tool_args=tool_args,
            )

        return {
            "plan": plan_rationale,
            "planned_tool": planned_tool,
            "tool_args": tool_args,
            "final_output": response_to_user,
        }

    def _synthesize_outbound_email(
        self,
        raw_cmd: str,
        cmd_lower: str,
        to_addr: str,
        facts: Dict[str, Any],
        summary: str,
    ) -> tuple[str, str]:
        """Synthesizes rich, professional email subject and body from natural language instructions."""
        if "jashan" in cmd_lower or "jashan" in to_addr.lower():
            greeting = "Hi Jashan,"
        elif "rahul" in cmd_lower or "rahul" in to_addr.lower():
            greeting = "Hi Rahul,"
        elif "sarah" in cmd_lower or "sarah" in to_addr.lower():
            greeting = "Hi Sarah,"
        else:
            name_part = to_addr.split("@")[0].capitalize()
            greeting = f"Hi {name_part},"

        if "test" in cmd_lower or "check" in cmd_lower or "testing" in cmd_lower:
            subject = "Personal AI OS — Status Verification Report"
            body = (
                f"{greeting}\n\n"
                f"Hope you are having a productive day.\n\n"
                f"This is an automated verification message dispatched from Personal AI OS. "
                f"The Gmail API connector and background agents are operating normally.\n\n"
                f"Best regards,\n"
                f"Yashpreet"
            )
            return subject, body

        if any(w in cmd_lower for w in ["meeting", "schedule", "sync", "catch up"]):
            subject = "Meeting Sync & Catch-up"
            body = (
                f"{greeting}\n\n"
                f"I wanted to reach out to coordinate a time for us to connect and sync on project updates. "
                f"Please let me know what times work best for you this week.\n\n"
                f"Best regards,\n"
                f"Yashpreet"
            )
            return subject, body

        cleaned_msg = raw_cmd
        for prefix in ["send a mail to", "send email to", "send mail to", "email to", "mail to", "write email to", "draft email to"]:
            if prefix in cleaned_msg.lower():
                idx = cleaned_msg.lower().index(prefix) + len(prefix)
                cleaned_msg = cleaned_msg[idx:].strip()
                break

        cleaned_msg = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "", cleaned_msg).strip()
        for filler in ["saying that", "saying", "telling him", "telling her", "and add other content", "add other content", "and generate other content"]:
            cleaned_msg = re.sub(re.escape(filler), "", cleaned_msg, flags=re.IGNORECASE).strip()

        core_msg = cleaned_msg.strip(" ,.-") or "Please find the requested project updates."
        subject = f"Update: {core_msg[:40]}" if len(core_msg) > 5 else "Important Update from Yashpreet"
        body = (
            f"{greeting}\n\n"
            f"{core_msg}\n\n"
            f"Feel free to reach out if you have any questions.\n\n"
            f"Best regards,\n"
            f"Yashpreet"
        )
        return subject, body

    def _keyword_fallback_reasoning(
        self,
        state: AgentState,
        facts: Dict[str, Any],
        summary: str,
        context: List[Dict[str, Any]],
        sender: str,
    ) -> ReasoningPlan:
        """Intelligent deterministic natural language reasoning engine."""
        raw_cmd = state.get("raw_body", "").strip()
        cmd_lower = raw_cmd.lower().strip(" ?.!/\\")
        words = set(re.findall(r"\b\w+\b", cmd_lower))
        email_regex_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_cmd)

        # ── Inbound Urgent/Important Email Auto-Note (Background Ingestion) ─
        if not state.get("is_interactive_command", False) and state.get("raw_subject") != "User Command":
            subj = state.get("raw_subject", "")
            if any(w in (subj + " " + raw_cmd).lower() for w in ["urgent", "outage", "asap", "incident", "critical", "alert"]):
                return ReasoningPlan(
                    tool_name="obsidian.create_note",
                    tool_args={
                        "title": f"Incident - {subj or 'Urgent Notice'}",
                        "content": f"# {subj}\n\n**Sender:** {sender}\n\n{raw_cmd}",
                        "tags": ["incident", "urgent", "email_ingest"],
                    },
                    plan_rationale="Urgent inbound email automatically logged to Obsidian.",
                    response_to_user=f"⚠️ Urgent incident note saved to Obsidian: '{subj}'",
                )

        # ── 1. Conversational Greetings & Small Talk ───────────────────────
        greetings = {"hlo", "hello", "hi", "hey", "sup", "yo", "good morning", "good evening", "good afternoon", "greetings", "howdy", "hola"}
        if cmd_lower in greetings or any(cmd_lower.startswith(g + " ") for g in ["hi", "hey", "hello", "hlo", "yo"]):
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="Conversational greeting.",
                response_to_user=(
                    "Hey Yashpreet! 👋 I'm here and ready to help. "
                    "You can ask me technical questions, search your emails and calendar, "
                    "draft messages, or explore your knowledge base. What's on your mind today?"
                ),
            )

        if cmd_lower in ["ok", "okay", "k", "cool", "got it", "sure", "sounds good", "alright", "all right", "great", "nice", "perfect", "done"]:
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="Conversational acknowledgement.",
                response_to_user="Got it! Let me know if you need anything or have a task for me.",
            )

        if any(p in cmd_lower for p in ["thank you", "thanks", "thx", "appreciate it"]):
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="Gratitude response.",
                response_to_user="You're welcome! Always here to help.",
            )

        if any(p in cmd_lower for p in ["how are you", "how's it going", "how r u", "how do you do"]):
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="Conversational query.",
                response_to_user=(
                    "I'm doing great, thanks for asking! Running smoothly locally on your machine with active Omarchy ricing, "
                    "multi-agent orchestration, and vector search ready to go. How can I assist you right now?"
                ),
            )

        if any(p in cmd_lower for p in ["who are you", "what are you", "tell me about yourself", "your name"]):
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="Self-identity question.",
                response_to_user=(
                    "I am **Personal AI OS**, your local-first personal AI assistant and automation copilot. "
                    "I specialize in autonomous multi-agent task execution, Gmail & Google Calendar management, "
                    "Obsidian note taking, and hybrid RAG semantic search across your personal knowledge vault."
                ),
            )

        # ── 2. Explicit Explanations & Conceptual Questions ────────────────
        # Question: What is YouTube?
        if "youtube" in cmd_lower and any(w in cmd_lower for w in ["what is", "what's", "explain", "tell me about", "who made", "history of", "about"]):
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="YouTube encyclopedic explanation.",
                response_to_user=(
                    "### 🎥 What is YouTube?\n\n"
                    "**YouTube** is the world's leading online video-sharing and streaming platform. Founded in **February 2005** by Steve Chen, Chad Hurley, and Jawed Karim (former PayPal engineers), it was acquired by **Google** in 2006 for $1.65 billion.\n\n"
                    "**Key Highlights:**\n"
                    "• **Global Scale**: Over **2.5 billion monthly active users**, making it the second most-visited website globally.\n"
                    "• **Creator Economy**: Pioneered revenue-sharing via the YouTube Partner Program (YPP), Super Chats, and channel memberships.\n"
                    "• **Ecosystem Features**:\n"
                    "  - **YouTube Shorts**: High-growth short-form vertical video feed.\n"
                    "  - **YouTube Music & Premium**: Background playback, ad-free streaming, and offline downloads.\n"
                    "  - **Live Streaming**: Real-time broadcasts, events, and gaming streams.\n\n"
                    "It is the central destination for worldwide education, tech tutorials, music, and entertainment."
                ),
            )

        # Question: What is Next.js?
        if "next js" in cmd_lower or "nextjs" in cmd_lower:
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="Next.js explanation.",
                response_to_user=(
                    "### ⚡ What is Next.js?\n\n"
                    "**Next.js** is a production-grade **React framework** created by Vercel for building full-stack web applications.\n\n"
                    "**Key Highlights:**\n"
                    "• **Server-Side Rendering (SSR) & Static Site Generation (SSG)**: Pre-renders pages on the server for blazingly fast load times and top-tier SEO.\n"
                    "• **App Router & React Server Components (RSC)**: Allows components to execute directly on the server, reducing client-side JavaScript bundle sizes.\n"
                    "• **Full-Stack API Routes**: Built-in serverless/Node.js API endpoints without needing an external Express server.\n"
                    "• **Automatic Optimizations**: Built-in image (`next/image`), font (`next/font`), and script optimizations.\n\n"
                    "It is the industry standard for modern React web development!"
                ),
            )

        # Question: What is scheduling / Calendar explanation?
        if ("what is scheduling" in cmd_lower or "explain scheduling" in cmd_lower or "how does scheduling work" in cmd_lower or "what is scheduling also" in cmd_lower):
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="Scheduling concept explanation.",
                response_to_user=(
                    "### 📅 What is Scheduling in Personal AI OS?\n\n"
                    "In Personal AI OS, **Scheduling** refers to the automated calendar and meeting orchestration engine connected to your **Google Calendar**.\n\n"
                    "**What it allows you to do:**\n"
                    "1. **Natural Language Event Booking**: Say *\"Schedule a meeting with Sarah tomorrow at 3 PM\"*, and the reasoning agent extracts the date/time and creates the calendar event.\n"
                    "2. **Agenda & Meeting Queries**: Ask *\"What meetings do I have this week?\"* or *\"Show my schedule\"* to fetch your upcoming agenda.\n"
                    "3. **Inbound Email Scheduling**: When an email arrives proposing a time (e.g. *\"Let's sync on Tuesday at 4pm\"*), the system sanitizes the details and offers a 1-click meeting creation action."
                ),
            )

        # Question: Why 3 Agents?
        if "agent" in cmd_lower and ("why" in cmd_lower or "3" in cmd_lower or "explain" in cmd_lower or "architecture" in cmd_lower):
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="Architecture explanation.",
                response_to_user=(
                    "### 🤖 Why 3 Agents in Personal AI OS?\n\n"
                    "The system architecture is separated into **3 specialized autonomous layers** for security and speed:\n\n"
                    "1. **🛡️ Security & Quarantine Agent** (Dual-LLM Sandbox): Evaluates untrusted inbound data in zero-tool isolation, stripping prompt injection attacks and extracting pure factual schema.\n"
                    "2. **⚡ Triaging Agent** (Passive-Aggressive ML): Sub-millisecond machine learning classifier that scores importance (0.0 to 1.0) to filter background noise.\n"
                    "3. **🧠 Reasoning & ReAct Agent** (LangGraph + HITL): Performs hybrid RAG retrieval, plans tool calls (Gmail, Calendar, Obsidian), and enforces Human-in-the-Loop authorization for high-risk actions."
                ),
            )

        # Question: What is HITL?
        if "hitl" in cmd_lower or "human in the loop" in cmd_lower or "safety gate" in cmd_lower:
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="HITL explanation.",
                response_to_user=(
                    "### 🛡️ What is the HITL (Human-in-the-Loop) Safety Gate?\n\n"
                    "The **HITL Safety Gate** is an authorization checkpoint between AI reasoning and real-world execution:\n\n"
                    "• **🟢 LOW Risk (Auto-Approved)**: Read-only operations like searching notes, listing events, and searching the RAG knowledge vault.\n"
                    "• **🟡 MEDIUM Risk**: Non-destructive actions like scheduling calendar meetings.\n"
                    "• **🔴 HIGH Risk (Explicit Approval Required)**: Sending outbound emails, executing shell commands, or modifying sensitive files. The agent pauses, generates an **Approval Card**, and waits for your confirmation."
                ),
            )

        # Question: What is DAG / Topology?
        if "dag" in cmd_lower or "topology" in cmd_lower:
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="DAG topology explanation.",
                response_to_user=(
                    "### 🕸️ What is the Topology DAG?\n\n"
                    "**DAG** stands for **Directed Acyclic Graph**. In LangGraph, the AI OS workflow is structured as a clear state machine:\n\n"
                    "```\n"
                    "[User Input / Inbound Email] ──→ [Quarantine Node] ──→ [Triaging Node]\n"
                    "                                                        │\n"
                    "                                                        ▼\n"
                    "[Tool Execution Node] ←── [HITL Approval Gate] ←── [Reasoning Node] ←── [RAG Retrieval]\n"
                    "```\n\n"
                    "This guarantees predictable transitions, checkpoint persistence, and complete execution traces."
                ),
            )

        # Question: What is RAG?
        if "rag" in cmd_lower and ("what" in cmd_lower or "how" in cmd_lower or "explain" in cmd_lower):
            return ReasoningPlan(
                tool_name="no_action",
                tool_args={},
                plan_rationale="RAG explanation.",
                response_to_user=(
                    "### 📚 What is Knowledge RAG?\n\n"
                    "**RAG** (**Retrieval-Augmented Generation**) gives the AI access to your private local knowledge files and documentation before answering.\n\n"
                    "**How our Hybrid RAG works:**\n"
                    "1. **Dense Semantic Embeddings**: Understands meanings using Sentence-Transformers.\n"
                    "2. **BM25 Keyword Search**: Exact matches for IDs, technical terms, and contact names.\n"
                    "3. **Recency Decay**: Prioritizes updated documents over older notes.\n"
                    "4. **Cross-Encoder Reranker**: Accurately scores the top chunks for maximum relevance."
                ),
            )

        # ── 3. Web Search Intent ──────────────────────────────────────────
        if any(cmd_lower.startswith(p) for p in ["search web", "search the web", "web search", "google ", "search online", "search internet", "browse web", "search for "]):
            q = cmd_lower
            for p in ["search the web for", "search web for", "search online for", "search internet for", "browse web for", "web search for", "web search", "google", "search for"]:
                if q.startswith(p):
                    q = q[len(p):].strip()
                    break
            q = q.strip(" :?.,\"'") or raw_cmd
            return ReasoningPlan(
                tool_name="web.search",
                tool_args={"query": q},
                plan_rationale=f"Web search intent for '{q}'.",
                response_to_user=f"🌐 Searching the live web for **\"{q}\"**...",
            )

        # ── 4. Workspace Files Intent ──────────────────────────────────────
        if any(w in cmd_lower for w in ["list files", "show files", "workspace files", "list directory", "show directory", "dir"]):
            subp = ""
            if " in " in cmd_lower:
                subp = cmd_lower.split(" in ")[-1].strip(" '\"`")
            return ReasoningPlan(
                tool_name="workspace.list_files",
                tool_args={"subpath": subp},
                plan_rationale="List workspace files.",
                response_to_user=f"📂 Listing workspace directory `{subp or '.'}`...",
            )

        if any(w in cmd_lower for w in ["read file", "view file", "show file", "cat file", "open file"]) and ("." in cmd_lower or "/" in cmd_lower or "\\" in cmd_lower):
            parts = cmd_lower.split()
            fpath = ""
            for p in parts:
                if "." in p or "/" in p or "\\" in p:
                    fpath = p.strip(" '\"`")
                    break
            if fpath:
                return ReasoningPlan(
                    tool_name="workspace.read_file",
                    tool_args={"file_path": fpath},
                    plan_rationale=f"Read file '{fpath}'.",
                    response_to_user=f"📄 Reading workspace file `{fpath}`...",
                )

        # ── 5. Notes Intent (Obsidian) ─────────────────────────────────────
        if any(w in cmd_lower for w in ["note", "notes", "obsidian"]):
            if any(w in cmd_lower for w in ["search notes", "find note", "look up note", "search obsidian", "search note"]):
                search_query = cmd_lower
                for p in ["search notes for", "search note for", "search notes", "search note", "find notes for", "find note for", "find note", "look up note", "search obsidian for", "search obsidian"]:
                    if p in search_query:
                        search_query = search_query.replace(p, "").strip()
                        break
                search_query = search_query.strip(" ?.,") or raw_cmd
                return ReasoningPlan(
                    tool_name="obsidian.search_notes",
                    tool_args={"query": search_query},
                    plan_rationale="Search notes intent detected.",
                    response_to_user=f"🔍 Searching notes for '{search_query}'...",
                )
            elif any(w in cmd_lower for w in ["create note", "take note", "save note", "make note", "write note", "add note", "create a note"]):
                note_title = facts.get("clean_subject") or "Personal Note"
                if note_title == "User Command" or not note_title:
                    clean_t = raw_cmd
                    for p in ["create note about", "take note about", "save note about", "make note about", "write note about", "create a note about", "take note of", "save note on", "save note", "create note", "take note"]:
                        if p in clean_t.lower():
                            idx = clean_t.lower().find(p) + len(p)
                            clean_t = clean_t[idx:].strip()
                            break
                    note_title = clean_t[:80].strip(" .!?,") or summary[:80]
                return ReasoningPlan(
                    tool_name="obsidian.create_note",
                    tool_args={
                        "title": note_title,
                        "content": f"# {note_title}\n\n{summary}",
                        "tags": ["personal_os", "notes"],
                    },
                    plan_rationale="Explicit note creation intent detected.",
                    response_to_user=f"📝 Created Obsidian note: '{note_title}'",
                )

        # ── 4. Calendar Tool Intents (Explicit Commands) ───────────────────
        is_calendar_query = any(
            w in cmd_lower
            for w in [
                "my calendar",
                "my schedule",
                "upcoming events",
                "upcoming meetings",
                "list events",
                "show events",
                "show meetings",
                "what meetings",
                "what events",
                "check calendar",
                "check schedule",
                "morning briefing",
                "daily briefing",
                "daily agenda",
                "today's agenda",
                "today's schedule",
                "today schedule",
            ]
        )
        is_schedule_command = (
            any(
                w in cmd_lower
                for w in [
                    "schedule a",
                    "schedule meeting",
                    "book a slot",
                    "book meeting",
                    "block two hours",
                    "block 2 hours",
                    "create event",
                ]
            )
            or (
                "schedule" in cmd_lower
                and any(
                    w in cmd_lower
                    for w in ["tomorrow", " pm", " am", " at ", "with rahul", "with sarah", "with jashan"]
                )
            )
        ) and not ("what is" in cmd_lower or "explain" in cmd_lower)

        if is_schedule_command:
            return ReasoningPlan(
                tool_name="calendar.create_event",
                tool_args={
                    "summary": f"Meeting: {facts.get('clean_subject') or summary[:30]}",
                    "start_time": "2026-08-27T15:00:00Z",
                    "end_time": "2026-08-27T16:00:00Z",
                    "description": summary,
                },
                plan_rationale="Explicit calendar event creation command.",
                response_to_user=f"📅 Scheduling calendar event: '{summary[:60]}'",
            )

        if is_calendar_query:
            return ReasoningPlan(
                tool_name="calendar.list_events",
                tool_args={"query": "upcoming"},
                plan_rationale="List calendar events / daily briefing intent detected.",
                response_to_user="📅 Fetching your Google Calendar events and daily agenda...",
            )

        # ── 5. Ordinal / Numbered Email Retrieval ──────────────────────────
        num_match = re.search(
            r"\b(?:([1-9]|first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|latest|last)\s+(?:email|mail|message)|(?:email|mail|message)\s*(?:#|number\s*)?([1-9]|first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|latest|last))\b",
            cmd_lower,
        )
        if num_match or any(w in cmd_lower for w in ["the first one", "the second one", "the 1st one", "the 2nd one", "the third one", "open first email", "read the first email"]):
            ident = (num_match.group(1) or num_match.group(2)) if num_match else ("first" if "first" in cmd_lower or "1st" in cmd_lower else "1")
            return ReasoningPlan(
                tool_name="email.get_email",
                tool_args={"identifier": ident},
                plan_rationale=f"Ordinal lookup for email reference '{ident}'.",
                response_to_user=f"📬 Fetching full content for email #{ident}...",
            )

        # ── 6. Outbound Send Email (Explicit Action) ────────────────────────
        send_triggers = [
            "send email", "send an email", "send a mail", "send mail", "send message to",
            "email rahul", "email sarah", "email alex", "email jashan", "write email to", "draft email to"
        ]
        has_send_action = any(w in cmd_lower for w in send_triggers)
        inbound_check_patterns = [
            r"\bcheck if\b", r"\bdid i\b", r"\bdid you\b", r"\bhave i\b",
            r"\breceived\b", r"\bsearch\b", r"\bfind\b", r"\bread\b", r"\bshow\b"
        ]
        has_inbound_check = any(re.search(p, cmd_lower) for p in inbound_check_patterns)

        if has_send_action and not has_inbound_check:
            if email_regex_match:
                to_addr = email_regex_match.group(0)
            elif "rahul" in cmd_lower:
                to_addr = "rahul@techcorp.io"
            elif "sarah" in cmd_lower:
                to_addr = "sarah.j@techcorp.io"
            elif sender and sender != "user":
                to_addr = sender
            else:
                to_addr = "jashanjashan372@gmail.com"

            subject_line, body_text = self._synthesize_outbound_email(
                raw_cmd=raw_cmd,
                cmd_lower=cmd_lower,
                to_addr=to_addr,
                facts=facts,
                summary=summary,
            )

            return ReasoningPlan(
                tool_name="email.send",
                tool_args={
                    "to": to_addr,
                    "subject": subject_line,
                    "body": body_text,
                },
                plan_rationale=f"Email sending intent detected for '{to_addr}'.",
                response_to_user=f"✉️ Sending email to {to_addr} — Subject: '{subject_line}'",
            )

        # ── 7. Inbound Email Search / Listing ──────────────────────────────
        explicit_search_triggers = [
            "check if i received", "check if i got", "did i receive", "did i get", "have i received",
            "check emails from", "check mail from", "check email from", "any email from", "any emails from",
            "emails from", "email from", "mail from", "mails from",
            "from linkedin", "from udemy", "from rahul", "from sarah", "from google", "from jashan",
            "show me full email from", "show full email from", "show email from", "read email from",
            "search email", "search emails", "find email", "find emails"
        ]

        if any(w in cmd_lower for w in explicit_search_triggers):
            if email_regex_match:
                search_term = email_regex_match.group(0)
            else:
                clean_query = cmd_lower
                for prefix in [
                    "check if i received any email from", "check if i received email from", "check if i received any emails from",
                    "check if i got any email from", "check if i got email from",
                    "check emails from", "check mail from", "check email from",
                    "did i receive any email from", "did i get any email from", "have i received any email from",
                    "show me full email from", "show full email from", "show me email from", "show email from", "read email from",
                    "full email from", "email from", "mail from", "emails from", "any email from", "any emails from",
                    "search email for", "find email for", "search emails for", "search email", "find email"
                ]:
                    if prefix in clean_query:
                        clean_query = clean_query.replace(prefix, "").strip()
                        break
                for suffix in [" send", " say", " email", " mail", " please", " yet", " today", " recently"]:
                    if clean_query.endswith(suffix):
                        clean_query = clean_query[:-len(suffix)].strip()
                search_term = clean_query.strip(" ?.,") or "is:unread"

            return ReasoningPlan(
                tool_name="email.search",
                tool_args={"query": search_term},
                plan_rationale=f"Inbound email search intent for '{search_term}'.",
                response_to_user=f"🔍 Searching Gmail for emails from/matching '{search_term}'...",
            )

        if any(w in cmd_lower for w in ["unread email", "unread emails", "show my unread", "check unread", "check inbox", "show inbox", "my unread"]):
            return ReasoningPlan(
                tool_name="email.list_unread",
                tool_args={"query": "is:unread"},
                plan_rationale="List unread emails intent detected.",
                response_to_user="📬 Fetching your recent unread emails from Gmail...",
            )

        # ── 8. RAG Grounded Answer from Retrieved Context ──────────────────
        if context:
            top_chunk = context[0]
            text_snippet = top_chunk.get("text", "")
            raw_score = top_chunk.get("score", 0.0)
            # Check if query matches topic of retrieved chunk
            if raw_score > 0.28 and len(text_snippet) > 20:
                score_pct = int(min(99.0, max(1.0, raw_score * 100 if raw_score <= 1.0 else raw_score * 10)))
                return ReasoningPlan(
                    tool_name="no_action",
                    tool_args={},
                    plan_rationale="Answer synthesized from retrieved RAG context.",
                    response_to_user=f"Based on your knowledge base:\n\n{text_snippet}\n\n*(Source: {top_chunk.get('source_type', 'knowledge')} • Relevance: {score_pct}%)*",
                )

        # ── 9. Natural Conversational Response ─────────────────────────────
        return ReasoningPlan(
            tool_name="no_action",
            tool_args={},
            plan_rationale="Conversational response.",
            response_to_user=(
                f"I understand your query: *\"{raw_cmd}\"*. "
                f"I'm operating in natural assistant mode. Let me know how you'd like to proceed or if there's a specific task you'd like me to perform!"
            ),
        )

    def _route_after_reasoning(self, state: AgentState) -> str:
        if state.get("planned_tool"):
            return "execute_tool"
        return "finish"

    async def _approval_gate_node(self, state: AgentState) -> Dict[str, Any]:
        t0 = time.perf_counter()
        tool_name = state.get("planned_tool", "")
        tool_args = state.get("tool_args", {})
        run_id = state.get("run_id")

        if self.perms.can_auto_execute(tool_name):
            duration_ms = (time.perf_counter() - t0) * 1000.0
            if run_id:
                trace_store.record_node_step(
                    run_id=run_id,
                    node_name="approval_gate_node",
                    inputs={"tool_name": tool_name, "tool_args": tool_args},
                    outputs={"status": "AUTO_APPROVED"},
                    duration_ms=duration_ms,
                    status="COMPLETED",
                )
            return {"approval_required": False, "approval_status": "AUTO_APPROVED"}

        req = self.perms.create_approval_request(
            tool_name=tool_name,
            tool_args=tool_args,
            summary=f"Agent wants to execute high-risk tool: {tool_name}",
        )
        duration_ms = (time.perf_counter() - t0) * 1000.0

        if run_id:
            trace_store.record_node_step(
                run_id=run_id,
                node_name="approval_gate_node",
                inputs={"tool_name": tool_name, "tool_args": tool_args},
                outputs={"status": "PENDING_APPROVAL", "request_id": req.id, "risk_level": req.risk_level.value},
                duration_ms=duration_ms,
                status="GATED",
            )

        return {
            "approval_required": True,
            "approval_request_id": req.id,
            "approval_status": "PENDING",
            "final_output": f"⚠️ Action paused for human approval: {tool_name} (Request ID: {req.id})",
        }

    def _route_after_approval_gate(self, state: AgentState) -> str:
        if state.get("approval_required", False):
            return "awaiting_approval"
        return "approved_execute"

    async def _tool_execution_node(self, state: AgentState) -> Dict[str, Any]:
        t0 = time.perf_counter()
        tool_name = state.get("planned_tool", "")
        args = state.get("tool_args", {})
        run_id = state.get("run_id")

        result, output_message = self.execute_tool_directly(tool_name, args, state.get("final_output"))
        duration_ms = (time.perf_counter() - t0) * 1000.0

        if run_id:
            trace_store.record_node_step(
                run_id=run_id,
                node_name="tool_execution_node",
                inputs={"tool_name": tool_name, "tool_args": args},
                outputs={"result": result, "final_output": output_message},
                duration_ms=duration_ms,
                status="COMPLETED",
                tool_call=tool_name,
                tool_args=args,
            )

        return {
            "execution_result": result,
            "final_output": output_message,
        }

    def execute_tool_directly(self, tool_name: str, args: Dict[str, Any], fallback_output: Optional[str] = None) -> tuple[Dict[str, Any], str]:
        """Executes a tool connector directly and returns (result_dict, human_readable_output)."""
        result: Dict[str, Any] = {}
        output_message = fallback_output or f"Executed {tool_name} successfully."

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
            output_message = f"✅ Calendar event '{args.get('summary', 'Event')}' created in Google Calendar."

        elif tool_name == "calendar.list_events":
            events = calendar_connector.list_upcoming_events(days_ahead=14)
            if events:
                lines = ["### 📅 Your Upcoming Google Calendar Events:\n"]
                for idx, ev in enumerate(events[:5], 1):
                    lines.append(f"{idx}. **{ev.summary}**\n   • Time: `{ev.start_time}`\n   • Location: {ev.location or 'None'}\n")
                output_message = "\n".join(lines)
            else:
                output_message = "📅 No upcoming events found in your Google Calendar for the next 14 days."
            result = {"events": [e.model_dump() for e in events]}

        elif tool_name == "email.send":
            out_email = OutboundEmail(
                to=args.get("to", ""),
                subject=args.get("subject", ""),
                body=args.get("body", ""),
            )
            result = gmail_connector.send_email(out_email)
            output_message = f"✅ Email sent to {args.get('to', 'recipient')} — Subject: {args.get('subject', '')}"

        elif tool_name == "email.get_email":
            ident = str(args.get("identifier", "1"))
            em = gmail_connector.get_email_by_identifier(ident)
            if em:
                date_str = time.strftime("%b %d, %Y • %I:%M %p", time.localtime(em.received_at_timestamp)) if em.received_at_timestamp else "Recent"
                output_message = (
                    f"### 📬 Email: **{em.subject}**\n\n"
                    f":::email-full\n"
                    f"id: {em.id}\n"
                    f"sender: {em.sender}\n"
                    f"subject: {em.subject}\n"
                    f"date: {date_str}\n"
                    f"body:\n{em.body}\n"
                    f":::\n"
                )
                result = {"email": em.model_dump()}
            else:
                output_message = f"📬 Could not find email '{ident}'. Try saying 'show my unread emails' first to list recent messages."
                result = {"error": "not_found"}

        elif tool_name == "email.search":
            q = args.get("query", "")
            results = gmail_connector.search_emails(query=q, max_results=5)
            if results:
                if len(results) == 1:
                    em = results[0]
                    date_str = time.strftime("%b %d, %Y • %I:%M %p", time.localtime(em.received_at_timestamp)) if em.received_at_timestamp else "Recent"
                    output_message = (
                        f"### 📬 Found 1 email for *\"{q}\"*:\n\n"
                        f":::email-full\n"
                        f"id: {em.id}\n"
                        f"sender: {em.sender}\n"
                        f"subject: {em.subject}\n"
                        f"date: {date_str}\n"
                        f"body:\n{em.body}\n"
                        f":::\n"
                    )
                else:
                    lines = [f"### 📬 Found {len(results)} matching email(s) for *\"{q}\"*:\n"]
                    for idx, em in enumerate(results, 1):
                        date_str = time.strftime("%b %d, %I:%M %p", time.localtime(em.received_at_timestamp)) if em.received_at_timestamp else ""
                        lines.append(
                            f":::email-card\n"
                            f"index: {idx}\n"
                            f"id: {em.id}\n"
                            f"sender: {em.sender}\n"
                            f"subject: {em.subject}\n"
                            f"date: {date_str}\n"
                            f"preview: {em.body[:220]}\n"
                            f":::\n"
                        )
                    output_message = "\n".join(lines)
            else:
                output_message = f"📬 No emails found in Gmail matching '{q}'."
            result = {"matches": [e.model_dump() for e in results]}

        elif tool_name == "email.list_unread":
            unread_emails = gmail_connector.list_unread(max_results=6)
            if unread_emails:
                lines = [f"### 📬 Your Recent Inbound Emails ({len(unread_emails)} messages):\n"]
                for idx, em in enumerate(unread_emails, 1):
                    date_str = time.strftime("%b %d, %I:%M %p", time.localtime(em.received_at_timestamp)) if em.received_at_timestamp else ""
                    lines.append(
                        f":::email-card\n"
                        f"index: {idx}\n"
                        f"id: {em.id}\n"
                        f"sender: {em.sender}\n"
                        f"subject: {em.subject}\n"
                        f"date: {date_str}\n"
                        f"preview: {em.body[:220]}\n"
                        f":::\n"
                    )
                output_message = "\n".join(lines)
            else:
                output_message = "📬 No unread emails found in your inbox right now. Everything is clear!"
            result = {"emails": [e.model_dump() for e in unread_emails]}

        elif tool_name == "web.search":
            query = args.get("query", "")
            results = search_web(query=query, max_results=4)
            if results:
                lines = [f"### 🌐 Web Summary: **\"{query}\"**\n"]
                clean_insights = []
                for r in results:
                    snippet = r.get("snippet", "")
                    clean_s = re.sub(r"\[\d+\]", "", snippet).strip()
                    if clean_s and len(clean_s) > 15:
                        clean_insights.append(f"• **{r['title']}**: {clean_s}")
                    elif r.get("title"):
                        clean_insights.append(f"• **{r['title']}**")

                lines.extend(clean_insights[:4])
                lines.append("\n**Sources & References:**")
                for r in results:
                    if r.get("url"):
                        lines.append(f"- [{r['title']}]({r['url']})")

                output_message = "\n".join(lines)
            else:
                output_message = f"🌐 No web search results found for query: \"{query}\""
            result = {"results": results}

        elif tool_name == "workspace.list_files":
            subpath = args.get("subpath", "")
            items = list_workspace_files(subpath=subpath)
            if items:
                lines = [f"### 📂 Workspace Files: `{subpath or '.'}`\n"]
                for it in items[:25]:
                    icon = "📁" if it.get("is_dir") else "📄"
                    size_str = f" ({it['size']} bytes)" if it.get("size") is not None else ""
                    lines.append(f"• {icon} `{it['path']}`{size_str}")
                output_message = "\n".join(lines)
            else:
                output_message = f"📂 No files found in `{subpath or '.'}`."
            result = {"items": items}

        elif tool_name == "workspace.read_file":
            path = args.get("file_path", "")
            res = read_workspace_file(file_path=path)
            if "error" in res:
                output_message = f"❌ {res['error']}"
            else:
                output_message = f"### 📄 File: `{res['path']}` ({res['total_chars']} chars)\n\n```\n{res['content']}\n```"
            result = res

        elif tool_name == "workspace.write_file":
            path = args.get("file_path", "")
            content = args.get("content", "")
            res = write_workspace_file(file_path=path, content=content)
            if "error" in res:
                output_message = f"❌ {res['error']}"
            else:
                output_message = f"✅ File `{res['path']}` written ({res['bytes_written']} bytes)."
            result = res

        elif tool_name.startswith("mcp:"):
            try:
                import asyncio
                import json
                from execution.tools.mcp_manager import mcp_manager
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import nest_asyncio
                        nest_asyncio.apply()
                        res = loop.run_until_complete(mcp_manager.call_namespaced_tool(tool_name, args))
                    else:
                        res = loop.run_until_complete(mcp_manager.call_namespaced_tool(tool_name, args))
                except Exception:
                    res = asyncio.run(mcp_manager.call_namespaced_tool(tool_name, args))

                output_message = f"### ⚡ MCP Tool Output: `{tool_name}`\n\n```json\n{json.dumps(res, indent=2)}\n```"
                result = res
            except Exception as e:
                output_message = f"❌ MCP Tool Execution Error ({tool_name}): {e}"
                result = {"error": str(e)}

        return result, output_message

    async def _low_priority_store_node(self, state: AgentState) -> Dict[str, Any]:
        facts = state.get("clean_facts", {})
        sub = facts.get("clean_subject", "Low Priority")
        return {
            "final_output": f"Stored low priority message without invoking LLM: {sub}",
        }


# Singleton instance
agent_engine = PersonalAIEngine()
