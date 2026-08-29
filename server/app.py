import asyncio
import io
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from execution.core.config import settings
from execution.core.llm_provider import llm_provider
from execution.ml.online_learner import online_learner
from execution.ml.triaging_classifier import triaging_classifier
from execution.orchestration.graph import agent_engine
from execution.orchestration.chat_history import (
    ChatMessage,
    ChatSession,
    chat_history_store,
)
from execution.orchestration.permission_manager import (
    ApprovalRequest,
    ApprovalStatus,
    permission_manager,
)
from execution.orchestration.trace_manager import trace_store
from execution.rag.hybrid_retriever import hybrid_retriever
from execution.rag.reranker import reranker
from execution.rag.vector_store import DocumentChunk, vector_store
from execution.tools.calendar_connector import CalendarEvent, calendar_connector
from execution.tools.gmail_connector import OutboundEmail, gmail_connector
from execution.tools.obsidian_connector import ObsidianNote, obsidian_connector
from execution.tools.deep_researcher import DeepResearcher
from execution.tools.folder_watcher import FolderWatcher

deep_researcher = DeepResearcher(vector_store=vector_store, llm_provider=llm_provider)
folder_watcher = FolderWatcher(vector_store=vector_store)

app = FastAPI(
    title="Personal AI OS",
    description="Local-first Personal AI Command Center and Automation Engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent inbox storage path
INBOX_STORAGE_PATH = settings.TEMP_DIR / "inbox_store.json"


def _load_inbox_store() -> List[Dict[str, Any]]:
    """Loads triaged inbox messages from disk or initializes seed emails if empty."""
    if INBOX_STORAGE_PATH.exists():
        try:
            data = json.loads(INBOX_STORAGE_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass

    # Baseline seed emails so inbox is immediately responsive on startup
    now = time.time()
    baseline = [
        {
            "id": "seed-em-01",
            "run_id": "seed-001",
            "sender": "sarah.j@techcorp.io",
            "subject": "Architecture Sync & Milestone Review",
            "body": "Hi Yashpreet,\n\nFollowing up on our sprint goals. Could we schedule a 30-minute sync this week to review the Personal AI OS multi-agent deployment and RAG pipeline integration?\n\nBest,\nSarah",
            "snippet": "Following up on our sprint goals. Could we schedule a 30-minute sync this week...",
            "category": "important",
            "category_label": "⚡ Important",
            "badge_color": "emerald",
            "is_read": False,
            "created_at": now - 3600,
        },
        {
            "id": "seed-em-02",
            "run_id": "seed-002",
            "sender": "careers@cloudscale.ai",
            "subject": "AI Systems Architect Position — Application Update",
            "body": "Hi Yashpreet,\n\nThank you for speaking with our engineering leadership team. We were very impressed by your autonomous agent architecture demonstration and would love to move forward to the technical design round.\n\nRegards,\nCloudScale Talent Team",
            "snippet": "Thank you for speaking with our engineering leadership team. We were very impressed...",
            "category": "job_career",
            "category_label": "💼 Career & Jobs",
            "badge_color": "cyan",
            "is_read": False,
            "created_at": now - 7200,
        },
        {
            "id": "seed-em-03",
            "run_id": "seed-003",
            "sender": "alerts@infra-monitor.net",
            "subject": "System Health Alert: Vector DB & Node Memory OK",
            "body": "All health checks passed. Memory utilization is at 14%, Qdrant vector index is optimal, and all local LLM worker nodes are responding within normal parameters.",
            "snippet": "All health checks passed. Memory utilization is at 14%, Qdrant vector index is optimal...",
            "category": "system_update",
            "category_label": "🔔 Updates & Alerts",
            "badge_color": "blue",
            "is_read": True,
            "created_at": now - 14400,
        },
    ]
    try:
        INBOX_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        INBOX_STORAGE_PATH.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    except Exception:
        pass
    return baseline


def _save_inbox_store():
    """Saves current triaged inbox to disk."""
    try:
        INBOX_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        INBOX_STORAGE_PATH.write_text(json.dumps(inbox_store, indent=2), encoding="utf-8")
    except Exception:
        pass


# In-memory fast cache loaded from disk
inbox_store: List[Dict[str, Any]] = _load_inbox_store()

# Knowledge Vault path
KNOWLEDGE_VAULT_DIR = Path(__file__).resolve().parent.parent / "directives" / "knowledge_vault"


def auto_index_sample_knowledge() -> int:
    """Indexes sample txt/md knowledge documents from directives/knowledge_vault into vector store."""
    if not KNOWLEDGE_VAULT_DIR.exists():
        return 0

    chunks: List[DocumentChunk] = []
    for file_path in KNOWLEDGE_VAULT_DIR.glob("*.*"):
        if file_path.suffix.lower() in [".txt", ".md", ".json"]:
            try:
                content = file_path.read_text(encoding="utf-8").strip()
                if not content:
                    continue

                # Split by sections or double newlines
                sections = content.split("\n\n")
                current_block = ""
                for sec in sections:
                    if len(current_block) + len(sec) < 500:
                        current_block += "\n\n" + sec if current_block else sec
                    else:
                        if current_block:
                            chunks.append(
                                DocumentChunk(
                                    text=current_block.strip(),
                                    source_type=f"file:{file_path.name}",
                                    metadata={"filename": file_path.name, "path": str(file_path)},
                                )
                            )
                        current_block = sec

                if current_block:
                    chunks.append(
                        DocumentChunk(
                            text=current_block.strip(),
                            source_type=f"file:{file_path.name}",
                            metadata={"filename": file_path.name, "path": str(file_path)},
                        )
                    )
            except Exception:
                pass

    if chunks:
        vector_store.insert_chunks(chunks)
    return len(chunks)


# Auto-index knowledge on module load
auto_index_sample_knowledge()


# Request / Response Schemas
class ChatCommandRequest(BaseModel):
    command: str
    thread_id: Optional[str] = None
    session_id: Optional[str] = None


class CreateChatSessionPayload(BaseModel):
    title: Optional[str] = "New Chat"


class UpdateChatSessionPayload(BaseModel):
    title: str


class InboundEmailPayload(BaseModel):
    subject: str
    body: str
    sender: str
    is_known_contact: bool = False


class EmailActionPayload(BaseModel):
    id: str
    action: str = Field(..., description="archive | mark_read | mark_unread | trash")


class DraftReplyRequest(BaseModel):
    id: Optional[str] = None
    sender: str
    subject: str
    body: str
    user_instructions: Optional[str] = None
    tone: Optional[str] = "professional"  # professional | concise | casual | friendly


class SendReplyPayload(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None
    msg_id: Optional[str] = None


class CreateCalendarEventPayload(BaseModel):
    summary: str
    start_time: str
    end_time: str
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)


class CreateObsidianNotePayload(BaseModel):
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    folder: Optional[str] = None


class DailyLogPayload(BaseModel):
    entry: str
    section: str = "AI Actions"


class ResolveApprovalPayload(BaseModel):
    approved: bool
    modified_args: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class SimulateApprovalPayload(BaseModel):
    tool_name: str = "email.send"
    tool_args: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class UpdatePoliciesPayload(BaseModel):
    require_high_risk: Optional[bool] = None
    auto_approve_low_risk: Optional[bool] = None
    auto_approve_medium_risk: Optional[bool] = None


class SimulateTracePayload(BaseModel):
    scenario: Optional[str] = "rag"  # rag | email_triage | calendar_event | obsidian_note | high_risk_gate


class SimulateGraphPayload(BaseModel):
    prompt: Optional[str] = None
    scenario: Optional[str] = "rag"


class FeedbackPayload(BaseModel):
    text: str
    user_label: int = Field(..., description="1 = Important, 0 = Unimportant")


class ComposeAssistRequest(BaseModel):
    to: Optional[str] = ""
    subject: Optional[str] = ""
    prompt: str
    tone: Optional[str] = "professional"  # professional | concise | friendly | urgent | executive
    key_points: Optional[List[str]] = Field(default_factory=list)


class ComposeSendPayload(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[List[str]] = Field(default_factory=list)
    is_draft: Optional[bool] = False

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "config": {
            "reasoning_model": settings.DEFAULT_REASONING_MODEL,
            "fast_model": settings.DEFAULT_FAST_MODEL,
            "embedding_model": settings.DEFAULT_EMBEDDING_MODEL,
            "qdrant_host": settings.QDRANT_HOST,
        },
    }


# ── Chat History Endpoints ──
@app.get("/api/chats")
async def list_chats(limit: int = 100):
    """List all local persistent chat sessions ordered by recency and pin status."""
    sessions = chat_history_store.list_sessions(limit=limit)
    return {"sessions": [s.model_dump() for s in sessions]}


@app.post("/api/chats")
async def create_chat(payload: Optional[CreateChatSessionPayload] = None):
    """Create a new local chat session."""
    title = payload.title if payload else "New Chat"
    session = chat_history_store.create_session(title=title)
    return {"session": session.model_dump()}


@app.get("/api/chats/{session_id}")
async def get_chat_history(session_id: str):
    """Retrieve metadata and complete message history for a specific chat session."""
    session = chat_history_store.get_session(session_id)
    if not session:
        session = chat_history_store.create_session(session_id=session_id)
    messages = chat_history_store.get_session_messages(session_id)
    return {
        "session": session.model_dump(),
        "messages": [m.model_dump() for m in messages],
    }


@app.put("/api/chats/{session_id}")
async def update_chat_session(session_id: str, payload: UpdateChatSessionPayload):
    """Rename a local chat session title."""
    ok = chat_history_store.update_session_title(session_id, payload.title)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    session = chat_history_store.get_session(session_id)
    return {"status": "updated", "session": session.model_dump() if session else None}


@app.post("/api/chats/{session_id}/pin")
async def toggle_pin_chat(session_id: str):
    """Toggle pin status for a local chat session."""
    ok = chat_history_store.toggle_pin_session(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    session = chat_history_store.get_session(session_id)
    return {"status": "updated", "session": session.model_dump() if session else None}


@app.delete("/api/chats/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session and all its associated messages permanently."""
    ok = chat_history_store.delete_session(session_id)
    return {"status": "deleted", "deleted": ok}


@app.delete("/api/chats")
async def clear_all_chats():
    """Clear all chat history from local SQLite store."""
    chat_history_store.clear_all_history()
    return {"status": "cleared"}


@app.post("/api/chat")
async def handle_chat_command(payload: ChatCommandRequest):
    """Processes natural language user requests through the LangGraph engine with persistent chat history and full trace capturing."""
    session_id = payload.session_id or f"session-{uuid.uuid4().hex[:8]}"
    thread_id = payload.thread_id or session_id
    config = {"configurable": {"thread_id": thread_id}}

    # Retrieve prior conversation turns for stateful multi-turn reasoning
    past_messages = chat_history_store.get_session_messages(session_id)
    history_tuples = [{"role": m.role, "content": m.content} for m in past_messages[-10:]]

    # Record user message in local SQLite history
    chat_history_store.add_message(session_id=session_id, role="user", content=payload.command)

    trace = trace_store.start_trace(query=payload.command, thread_id=thread_id, sender="user")

    initial_state = {
        "run_id": trace.run_id,
        "raw_subject": "User Command",
        "raw_body": payload.command,
        "sender": "user",
        "is_known_contact": True,
        "is_interactive_command": True,
        "chat_history": history_tuples,
    }

    try:
        result = await agent_engine.app.ainvoke(initial_state, config=config)
        final_output = result.get("final_output", "Processed.")
        planned_tool = result.get("planned_tool")
        tool_args = result.get("tool_args")
        approval_req = result.get("approval_required", False)
        approval_id = result.get("approval_request_id")

        trace_store.complete_trace(
            run_id=trace.run_id,
            status="AWAITING_APPROVAL" if approval_req else "SUCCESS",
            final_output=final_output,
            planned_tool=planned_tool,
            tool_args=tool_args,
            approval_required=approval_req,
            approval_request_id=approval_id,
        )

        # Record assistant response in local SQLite history
        chat_history_store.add_message(
            session_id=session_id,
            role="assistant",
            content=final_output,
            run_id=trace.run_id,
            planned_tool=planned_tool,
            tool_args=tool_args,
            approval_required=approval_req,
            approval_request_id=approval_id,
        )

        # Continuously ingest conversation Q&A into hybrid vector RAG store
        try:
            qa_summary = f"User Query: {payload.command}\nPersonal AI Response: {final_output}"
            if planned_tool and planned_tool != "no_action":
                qa_summary += f"\nAction Performed: {planned_tool} with parameters {tool_args}"
            vector_store.insert_chunks([
                DocumentChunk(
                    text=qa_summary,
                    source_type="chat_interaction",
                    metadata={
                        "session_id": session_id,
                        "run_id": trace.run_id,
                        "timestamp": time.time(),
                        "query": payload.command,
                    },
                )
            ])
        except Exception:
            pass

        return {
            "session_id": session_id,
            "run_id": trace.run_id,
            "thread_id": thread_id,
            "final_output": final_output,
            "planned_tool": planned_tool,
            "tool_args": tool_args,
            "approval_required": approval_req,
            "approval_request_id": approval_id,
        }
    except Exception as e:
        trace_store.complete_trace(run_id=trace.run_id, status="ERROR", error=str(e))
        chat_history_store.add_message(session_id=session_id, role="assistant", content=f"⚠️ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/inbox/ingest")
async def ingest_inbound_email(payload: InboundEmailPayload):
    """Ingests an email, sanitizes via Dual-LLM quarantine, triages via ML, and records trace."""
    thread_id = f"email-{uuid.uuid4().hex[:6]}"
    config = {"configurable": {"thread_id": thread_id}}

    trace = trace_store.start_trace(
        query=f"[{payload.subject}] {payload.body}", thread_id=thread_id, sender=payload.sender
    )

    initial_state = {
        "run_id": trace.run_id,
        "raw_subject": payload.subject,
        "raw_body": payload.body,
        "sender": payload.sender,
        "is_known_contact": payload.is_known_contact,
    }

    result = await agent_engine.app.ainvoke(initial_state, config=config)
    final_out = result.get("final_output", "")
    planned_t = result.get("planned_tool")
    app_req = result.get("approval_required", False)
    app_id = result.get("approval_request_id")

    trace_store.complete_trace(
        run_id=trace.run_id,
        status="AWAITING_APPROVAL" if app_req else "SUCCESS",
        final_output=final_out,
        planned_tool=planned_t,
        tool_args=result.get("tool_args"),
        approval_required=app_req,
        approval_request_id=app_id,
    )

    inbox_item = {
        "id": thread_id,
        "run_id": trace.run_id,
        "sender": payload.sender,
        "subject": payload.subject,
        "body": payload.body,
        "clean_facts": result.get("clean_facts", {}),
        "triage": result.get("triage", {}),
        "approval_required": app_req,
        "approval_request_id": app_id,
        "final_output": final_out,
        "created_at": time.time(),
    }
    inbox_store.insert(0, inbox_item)
    _save_inbox_store()

    # Index into vector store for subsequent RAG retrieval
    vector_store.insert_chunks([
        DocumentChunk(
            text=f"Subject: {payload.subject}\n\n{payload.body}",
            source_type="email",
            metadata={"sender": payload.sender, "thread_id": thread_id},
        )
    ])

    return inbox_item


@app.post("/api/inbox/sync")
async def sync_live_gmail():
    """Fetches emails directly from Gmail API (inbox + unread), runs triage & quarantine, and populates inbox."""
    try:
        inbox_emails = await asyncio.to_thread(gmail_connector.list_inbox_messages, 35)
        existing_ids = {item.get("id") for item in inbox_store}
        new_count = 0

        for em in inbox_emails:
            if em.id in existing_ids:
                continue

            email_data = {
                "sender": em.sender,
                "subject": em.subject,
                "body": em.body,
                "is_known_contact": False,
            }
            pred = triaging_classifier.predict(email_data)
            pred_dict = pred.model_dump()

            inbox_item = {
                "id": em.id,
                "run_id": f"sync-{em.id[:8]}",
                "sender": em.sender,
                "subject": em.subject or "No Subject",
                "body": em.body,
                "snippet": pred.clean_snippet or (em.body[:120] if em.body else "No preview available"),
                "category": pred.predicted_category,
                "category_label": pred.category_label,
                "badge_color": pred.badge_color,
                "is_read": getattr(em, "is_read", False),
                "clean_facts": {
                    "clean_subject": em.subject,
                    "factual_summary": pred.clean_snippet,
                    "is_suspicious_or_adversarial": pred.predicted_category == "likely_scam",
                },
                "triage": pred_dict,
                "approval_required": False,
                "approval_request_id": None,
                "final_output": em.body[:300],
                "created_at": em.received_at_timestamp or time.time(),
            }
            inbox_store.insert(0, inbox_item)
            new_count += 1

        # Keep inbox sorted newest first
        inbox_store.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        _save_inbox_store()

        return {"status": "synced", "total_inbox": len(inbox_store), "new_synced": new_count}
    except Exception as e:
        return {"status": "error", "error": str(e), "total_inbox": len(inbox_store)}


@app.get("/api/inbox")
async def list_inbox():
    """Retrieve all triaged inbound messages instantly from fast persistent cache."""
    return {"inbox": inbox_store}


@app.post("/api/inbox/action")
async def handle_inbox_action(payload: EmailActionPayload):
    """Performs archive, mark_read, mark_unread, or trash on an inbox email."""
    act = payload.action.lower()
    msg_id = payload.id
    res = {}
    if act == "archive":
        res = gmail_connector.archive_message(msg_id)
        for item in inbox_store:
            if item.get("id") == msg_id:
                item["is_archived"] = True
    elif act == "mark_read":
        res = gmail_connector.mark_as_read(msg_id)
        for item in inbox_store:
            if item.get("id") == msg_id:
                item["is_read"] = True
    elif act == "mark_unread":
        res = gmail_connector.mark_as_unread(msg_id)
        for item in inbox_store:
            if item.get("id") == msg_id:
                item["is_read"] = False
    elif act == "trash":
        res = gmail_connector.trash_message(msg_id)
        inbox_store[:] = [item for item in inbox_store if item.get("id") != msg_id]
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {payload.action}")

    _save_inbox_store()
    await ws_manager.broadcast({"type": "inbox_update"})
    return {"status": "success", "action": act, "result": res}


@app.post("/api/inbox/draft-reply")
async def draft_ai_reply(payload: DraftReplyRequest):
    """Generates an intelligent context-aware reply draft using the fast/reasoning LLM."""
    try:
        tone_guide = {
            "professional": "Polite, clear, concise, professional tone.",
            "concise": "Extremely brief, direct to the point, no fluff (2-3 sentences max).",
            "casual": "Warm, conversational, and helpful tone.",
            "friendly": "Encouraging, friendly, and collaborative tone.",
        }.get(payload.tone or "professional", "Polite, professional tone.")

        prompt = (
            f"You are the AI Executive Assistant for the user. Draft an email reply.\n"
            f"Original Sender: {payload.sender}\n"
            f"Original Subject: {payload.subject}\n"
            f"Original Email Body:\n{payload.body[:1500]}\n\n"
            f"Style/Tone: {tone_guide}\n"
        )
        if payload.user_instructions:
            prompt += f"User Directives: {payload.user_instructions}\n"
        prompt += (
            "\nOutput ONLY the body text of the draft email response. Do not include placeholder brackets like [Your Name] if possible (sign off simply or as 'Best regards')."
        )

        try:
            res = await llm_provider.generate(prompt=prompt)
            draft_text = res.content.strip()
        except Exception:
            draft_text = f"Hi,\n\nThank you for reaching out regarding '{payload.subject}'. I have received your message and will follow up shortly.\n\nBest regards,\nYashpreet"

        reply_subject = payload.subject if payload.subject.lower().startswith("re:") else f"Re: {payload.subject}"
        return {
            "status": "success",
            "to": payload.sender,
            "subject": reply_subject,
            "body": draft_text.strip(),
            "tone": payload.tone,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate draft: {str(e)}")


@app.post("/api/inbox/send-reply")
async def send_inbox_reply(payload: SendReplyPayload):
    """Sends a threaded email reply directly via Gmail API."""
    try:
        res = gmail_connector.send_reply(
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            thread_id=payload.thread_id,
        )
        if payload.msg_id:
            gmail_connector.mark_as_read(payload.msg_id)
            for item in inbox_store:
                if item.get("id") == payload.msg_id:
                    item["is_read"] = True
                    item["has_replied"] = True

        await ws_manager.broadcast({"type": "inbox_update"})
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {str(e)}")


@app.get("/api/inbox/sent")
async def list_sent_emails(max_results: int = 35):
    """Retrieve recent sent messages from Gmail."""
    try:
        sent = await asyncio.to_thread(gmail_connector.list_sent_messages, max_results)
        return {"status": "success", "sent": sent, "count": len(sent)}
    except Exception as e:
        return {"status": "error", "error": str(e), "sent": []}


@app.post("/api/inbox/compose/ai-assist")
async def ai_compose_email(payload: ComposeAssistRequest):
    """Generates an intelligent email draft with subject & body using LLM."""
    try:
        tone_instructions = {
            "professional": "Polite, articulate, well-structured, professional business tone.",
            "concise": "Crisp, direct, action-oriented, under 4 sentences.",
            "friendly": "Warm, collaborative, enthusiastic, and approachable tone.",
            "urgent": "Time-sensitive, clear deadline, direct call to action.",
            "executive": "High-level executive summary, strategic, clear decision points.",
        }.get(payload.tone or "professional", "Professional tone.")

        sys_prompt = (
            "You are Personal AI OS, an expert executive communication assistant.\n"
            "Draft a complete, polished outbound email based on the user's intent.\n"
            "You must return a JSON object with strictly two keys:\n"
            "  - `subject`: A clear, compelling email subject line.\n"
            "  - `body`: The full formatted body text of the email with appropriate greeting, paragraphs, bullet points if needed, and professional sign-off (sign as Yashpreet).\n"
            "Do NOT include any markdown fences or commentary outside the JSON."
        )

        user_content = (
            f"Recipient: {payload.to or 'Not specified'}\n"
            f"User Prompt/Intent: {payload.prompt}\n"
            f"Style & Tone: {tone_instructions}\n"
        )
        if payload.subject:
            user_content += f"Existing Subject Reference: {payload.subject}\n"
        if payload.key_points:
            user_content += f"Key Points to Include:\n" + "\n".join([f"- {kp}" for kp in payload.key_points]) + "\n"

        class EmailDraftOutput(BaseModel):
            subject: str = Field(..., description="Email subject line")
            body: str = Field(..., description="Email body content")

        try:
            structured_res = await llm_provider.generate_structured(
                schema=EmailDraftOutput,
                prompt=user_content,
                system_prompt=sys_prompt,
            )
            subj = structured_res.subject
            body = structured_res.body
        except Exception:
            try:
                # Fallback to plain generation
                raw_gen = await llm_provider.generate(
                    prompt=f"{sys_prompt}\n\n{user_content}\nDraft the subject and body:",
                )
                raw_text = raw_gen.content.strip()
                subj = payload.subject or "Update from Yashpreet"
                body = raw_text
                if "subject:" in raw_text.lower():
                    lines = raw_text.splitlines()
                    for idx, line in enumerate(lines):
                        if line.lower().startswith("subject:"):
                            subj = line.split(":", 1)[1].strip()
                            body = "\n".join(lines[idx + 1:]).strip()
                            break
            except Exception:
                subj = payload.subject or f"Regarding: {payload.prompt[:40]}"
                body = f"Hi,\n\nFollowing up on: {payload.prompt}\n\nPlease let me know your thoughts.\n\nBest regards,\nYashpreet"

        return {
            "status": "success",
            "to": payload.to,
            "subject": subj,
            "body": body,
            "tone": payload.tone,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Compose failed: {str(e)}")


@app.post("/api/inbox/compose/send")
async def send_composed_email(payload: ComposeSendPayload):
    """Sends or saves an outbound email composed by the user."""
    try:
        outbound = OutboundEmail(
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            cc=payload.cc or [],
        )
        if payload.is_draft:
            res = gmail_connector.create_draft(outbound)
            return {"status": "success", "mode": "draft", "result": res}
        else:
            res = gmail_connector.send_email(outbound)
            await ws_manager.broadcast({"type": "inbox_update"})
            return {"status": "success", "mode": "sent", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@app.get("/api/calendar/events")
async def list_calendar_events(
    days_back: int = 120,
    days_ahead: int = 365,
    include_festivals: bool = True,
):
    """Lists calendar events and cultural festivals across past, present, and future ranges."""
    try:
        events = await asyncio.to_thread(
            calendar_connector.list_upcoming_events,
            days_back,
            days_ahead,
            include_festivals,
        )
        return {"status": "success", "events": [e.model_dump() for e in events]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {str(e)}")


@app.get("/api/calendar/festivals")
async def list_festivals(year: Optional[int] = None):
    """Returns curated cultural and public festivals for a year."""
    try:
        festivals = await asyncio.to_thread(calendar_connector.list_festivals, year)
        return {"status": "success", "festivals": [f.model_dump() for f in festivals]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch festivals: {str(e)}")


@app.post("/api/calendar/create")
async def create_calendar_event(payload: CreateCalendarEventPayload):
    """Creates a new event in Google Calendar with offline persistent fallback."""
    try:
        ev = CalendarEvent(
            summary=payload.summary,
            start_time=payload.start_time,
            end_time=payload.end_time,
            description=payload.description,
            location=payload.location,
            attendees=payload.attendees,
        )
        res = await asyncio.to_thread(calendar_connector.create_event, ev)
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@app.delete("/api/calendar/event")
async def delete_calendar_event(event_id: str):
    """Deletes a calendar event by ID."""
    try:
        deleted = await asyncio.to_thread(calendar_connector.delete_event, event_id)
        return {"status": "success", "deleted": deleted, "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")


# ── Obsidian Vault Endpoints ──

@app.get("/api/obsidian/status")
async def get_obsidian_status():
    """Returns Obsidian vault connection status, location path, and note stats."""
    vault_path = obsidian_connector.vault_path
    notes = await asyncio.to_thread(obsidian_connector.list_all_notes)
    folders = list(set(n["folder"] for n in notes))
    all_tags = sorted(list(set(t for n in notes for t in n.get("tags", []))))
    return {
        "status": "connected" if vault_path.exists() else "not_found",
        "vault_path": str(vault_path),
        "total_notes": len(notes),
        "folders": sorted(folders),
        "tags": all_tags,
    }


@app.get("/api/obsidian/notes")
async def list_obsidian_notes(folder: Optional[str] = None, tag: Optional[str] = None):
    """Lists notes with optional folder or tag filtering."""
    notes = await asyncio.to_thread(obsidian_connector.list_all_notes)
    if folder and folder.lower() != "all":
        notes = [n for n in notes if n["folder"].lower() == folder.lower()]
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]
    return {
        "notes": notes,
        "vault_path": str(obsidian_connector.vault_path),
        "total": len(notes),
    }


@app.get("/api/obsidian/note")
async def get_obsidian_note(path: str):
    """Reads a specific note content and metadata."""
    note = obsidian_connector.read_note(path)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found in Obsidian vault")
    return {"note": note}


@app.post("/api/obsidian/note")
async def create_or_update_obsidian_note(payload: CreateObsidianNotePayload):
    """Creates or updates a note file in the Obsidian vault."""
    try:
        note_obj = ObsidianNote(
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
            folder=payload.folder,
        )
        res = obsidian_connector.create_or_update_note(note_obj)
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create note: {str(e)}")


@app.post("/api/obsidian/daily-log")
async def append_obsidian_daily_log(payload: DailyLogPayload):
    """Appends an entry to today's Obsidian daily note."""
    try:
        res = obsidian_connector.append_daily_log(payload.entry, section=payload.section)
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to append daily log: {str(e)}")


@app.delete("/api/obsidian/note")
async def delete_obsidian_note(path: str):
    """Deletes a note from the Obsidian vault."""
    deleted = obsidian_connector.delete_note(path)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note file could not be deleted or was not found")
    return {"status": "success", "deleted_path": path}


@app.get("/api/approvals")
async def list_approvals():
    """List pending High-Risk Human-in-the-Loop approvals."""
    return {"pending_approvals": [req.model_dump() for req in permission_manager.list_pending_requests()]}


@app.get("/api/approvals/history")
async def list_approval_history(limit: int = 50):
    """List resolved approval requests audit log."""
    return {"history": [req.model_dump() for req in permission_manager.list_history(limit=limit)]}


@app.post("/api/approvals/history/clear")
async def clear_approval_history():
    """Clears the resolved approval audit log."""
    permission_manager.clear_history()
    return {"status": "cleared"}


@app.get("/api/approvals/policies")
async def get_approval_policies():
    """Get active safety and permission policies."""
    return {"policies": permission_manager.get_policies()}


@app.post("/api/approvals/policies")
async def update_approval_policies(payload: UpdatePoliciesPayload):
    """Update active safety and permission policies."""
    updates = {}
    if payload.require_high_risk is not None:
        updates["require_high_risk"] = payload.require_high_risk
    if payload.auto_approve_low_risk is not None:
        updates["auto_approve_low_risk"] = payload.auto_approve_low_risk
    if payload.auto_approve_medium_risk is not None:
        updates["auto_approve_medium_risk"] = payload.auto_approve_medium_risk
    updated = permission_manager.update_policies(updates)
    return {"status": "updated", "policies": updated}


@app.post("/api/approvals/simulate")
async def simulate_approval(payload: SimulateApprovalPayload):
    """Simulates a high-risk tool call intercepted by the HITL safety gate for UI testing."""
    tool_name = payload.tool_name or "email.send"
    tool_args = payload.tool_args or {
        "to": "partner@critical-client.com",
        "subject": "Confidential Q3 Project Architecture Blueprint",
        "body": "Hi team, attached is the full confidential project architecture blueprint and API specification for our review.",
    }
    summary = payload.summary or f"Agent attempted to execute high-risk tool '{tool_name}' targeting external contact."
    req = permission_manager.create_approval_request(
        tool_name=tool_name,
        tool_args=tool_args,
        summary=summary,
    )
    return {"status": "created", "request": req.model_dump()}


@app.post("/api/approvals/{request_id}/resolve")
async def resolve_approval(request_id: str, payload: ResolveApprovalPayload):
    """Approve or reject a pending high-risk tool execution."""
    execution_output = None
    if payload.approved:
        # Check if modified arguments were provided
        req = permission_manager._approval_queue.get(request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Approval request not found")
        
        args_to_use = payload.modified_args if payload.modified_args is not None else req.tool_args
        _, output_msg = agent_engine.execute_tool_directly(req.tool_name, args_to_use)
        execution_output = output_msg

    resolved = permission_manager.resolve_request(
        request_id=request_id,
        approved=payload.approved,
        edited_args=payload.modified_args,
        notes=payload.notes,
        execution_result=execution_output,
    )
    if not resolved:
        raise HTTPException(status_code=404, detail="Approval request not found")

    return {
        "status": "resolved",
        "request": resolved.model_dump(),
        "execution_output": execution_output,
    }



@app.post("/api/feedback")
async def submit_feedback(payload: FeedbackPayload):
    """Submit online learning correction to update model weights incrementally."""
    updated_prob = online_learner.learn_one(payload.text, label=payload.user_label)
    return {
        "status": "updated",
        "update_count": online_learner.update_count,
        "new_calibrated_probability": updated_prob,
    }


@app.get("/api/rag/search")
async def rag_search(q: str, top_k: int = 5):
    """Semantic search over the personal knowledge base via hybrid RAG."""
    if not q.strip():
        return {"results": []}
    candidates = hybrid_retriever.search(query=q, top_k=top_k * 2)
    reranked = reranker.rerank(query=q, candidates=candidates, top_n=top_k)
    return {
        "query": q,
        "results": [
            {
                "text": c.text,
                "source_type": c.source_type,
                "score": c.score,
                "score_breakdown": c.metadata.get("score_breakdown", {}),
            }
            for c in reranked
        ],
    }


@app.get("/api/rag/files")
async def list_sample_knowledge_files():
    """List sample knowledge files available in directives/knowledge_vault/."""
    files = []
    if KNOWLEDGE_VAULT_DIR.exists():
        for fp in KNOWLEDGE_VAULT_DIR.glob("*.*"):
            if fp.suffix.lower() in [".txt", ".md", ".json", ".pdf"]:
                files.append({"name": fp.name, "size": fp.stat().st_size, "path": str(fp)})
    return {"files": files}


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a PDF, CSV, or document to the drop folder and processes it immediately via universal ingestion."""
    try:
        drop_path = folder_watcher.drop_dir / (file.filename or "uploaded_file.txt")
        content = await file.read()
        drop_path.write_bytes(content)
        result = folder_watcher.process_file(drop_path, force=True)
        if result:
            return {
                "status": "success",
                "filename": file.filename,
                "document": result,
                "total_chars": result.get("filesize_bytes", len(content)),
                "chunks_indexed": 1,
                "preview": result.get("summary", "")[:300]
            }
        return {"status": "error", "detail": "Failed to parse document"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Active WebSocket Connection Manager & Broadcast ────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        dead_connections = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for dc in dead_connections:
            self.disconnect(dc)


ws_manager = ConnectionManager()


# Register TraceStore listener to push real-time DAG node executions across WebSockets
def _broadcast_trace_event(event_type: str, data: Dict[str, Any]):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(ws_manager.broadcast({
                "type": "trace_event",
                "event": event_type,
                "data": data,
            }))
    except Exception:
        pass

trace_store.add_listener(_broadcast_trace_event)


# ── Proactive Background Autonomous Worker ─────────────────────────────────

_alerted_email_ids = set()

async def proactive_background_worker():
    """Periodically scans for urgent inbox items, syncs them to inbox_store, and pushes proactive alerts."""
    await asyncio.sleep(8)
    while True:
        try:
            from execution.tools.gmail_connector import gmail_connector
            recent = await asyncio.to_thread(gmail_connector.list_inbox_messages, 15)
            new_incoming = False
            for em in recent:
                if em.id not in _alerted_email_ids:
                    _alerted_email_ids.add(em.id)
                    new_incoming = True
                    # Broadcast proactive toast alert to dashboard if unread
                    if not getattr(em, "is_read", False):
                        await ws_manager.broadcast({
                            "type": "proactive_alert",
                            "title": f"📬 Inbound Email: {em.subject[:45]}",
                            "message": f"From: {em.sender}\n{em.body[:140]}...",
                            "sender": em.sender,
                            "email_id": em.id,
                            "timestamp": time.time()
                        })
            if new_incoming:
                await sync_live_gmail()
                await ws_manager.broadcast({"type": "inbox_update"})
        except Exception:
            pass
        await asyncio.sleep(30)


@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(proactive_background_worker())
    folder_watcher.start_background_watcher(interval_seconds=10)


class ResearchPayload(BaseModel):
    topic: str
    depth: int = 2


@app.post("/api/research/run")
async def run_deep_research(payload: ResearchPayload):
    """Executes deep autonomous research across multiple web sources and compiles a dossier."""
    run_id = f"res-{uuid.uuid4().hex[:8]}"
    trace_store.start_trace(run_id=run_id, thread_id="research-thread", query=f"Deep Research: {payload.topic}", sender="user")
    try:
        trace_store.record_node_step(
            run_id=run_id,
            node_name="research_decomposition",
            inputs={"topic": payload.topic, "depth": payload.depth},
            outputs={"status": "sub_queries_generated"},
            duration_ms=12.0,
            status="COMPLETED"
        )
        dossier = deep_researcher.conduct_research(topic=payload.topic, depth=payload.depth)
        trace_store.finish_trace(
            run_id=run_id,
            status="SUCCESS",
            planned_tool="deep_research.conduct",
            tool_args={"topic": payload.topic, "depth": payload.depth},
            final_output=f"🔬 Deep research compiled for '{payload.topic}' with {len(dossier.get('sections', []))} sections and {len(dossier.get('sources', []))} sources."
        )
        return {"status": "success", "dossier": dossier}
    except Exception as e:
        trace_store.complete_trace(run_id=run_id, status="ERROR", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/research/history")
async def get_research_history():
    """Lists all compiled research dossiers from Obsidian vault."""
    research_dir = obsidian_connector.vault_path / "Research"
    res_list = []
    if research_dir.exists():
        for p in sorted(research_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                txt = p.read_text(encoding="utf-8", errors="replace")
                lines = [l for l in txt.splitlines() if l.strip()]
                preview = txt[:250]
                res_list.append({
                    "title": p.stem,
                    "filename": p.name,
                    "filepath": str(p),
                    "modified": p.stat().st_mtime,
                    "preview": preview
                })
            except Exception:
                pass
    return {"history": res_list}


@app.get("/api/research/dossier")
async def get_research_dossier(filename: str):
    """Retrieves full text and parsed metadata of a specific research dossier."""
    research_dir = obsidian_connector.vault_path / "Research"
    target_file = research_dir / filename
    if not target_file.exists() or not target_file.is_file():
        # Try matching by stem or safe search
        matched = list(research_dir.glob(f"*{filename}*"))
        if matched and matched[0].is_file():
            target_file = matched[0]
        else:
            raise HTTPException(status_code=404, detail=f"Dossier '{filename}' not found")

    content = target_file.read_text(encoding="utf-8", errors="replace")
    return {
        "filename": target_file.name,
        "title": target_file.stem,
        "filepath": str(target_file),
        "modified": target_file.stat().st_mtime,
        "content": content
    }


@app.get("/api/documents")
async def list_documents():
    """List all ingested documents and their extracted metadata."""
    docs = folder_watcher.list_processed_documents()
    return {"documents": docs, "total_count": len(docs)}


@app.post("/api/documents/sync")
async def sync_documents():
    """Trigger manual scan and ingestion for all files in drop directory."""
    new_docs = folder_watcher.scan_and_ingest_all()
    return {"status": "success", "newly_processed": len(new_docs), "documents": new_docs}


@app.get("/api/spotlight/search")
async def spotlight_search(q: str = ""):
    """Unified spotlight search across Quick Actions, Vault Notes, Documents, and AI Prompts."""
    query = q.strip().lower()
    
    default_actions = [
        {"id": "act-res", "title": "🔬 Deep Research Topic", "category": "action", "description": "Run autonomous multi-step research and build an Obsidian dossier", "shortcut": "R", "command": "open_tab", "payload": {"tab": "research"}},
        {"id": "act-brief", "title": "🌅 Generate Daily Briefing", "category": "action", "description": "Synthesize today's schedule, urgent emails & tasks", "shortcut": "B", "command": "trigger_briefing"},
        {"id": "act-docs", "title": "📂 Ingest Drop Folder Documents", "category": "action", "description": "Scan and parse PDFs, CSVs, and notes in inbox drop", "shortcut": "D", "command": "open_tab", "payload": {"tab": "documents"}},
        {"id": "act-cal", "title": "📅 New Calendar Event", "category": "action", "description": "Quickly schedule an event or meeting", "shortcut": "C", "command": "open_tab", "payload": {"tab": "schedule"}},
        {"id": "act-inbox", "title": "📬 Open Smart Inbox", "category": "action", "description": "View ML categorized emails and smart reply drafts", "shortcut": "I", "command": "open_tab", "payload": {"tab": "inbox"}},
        {"id": "act-trace", "title": "⚡ Open Execution Traces", "category": "action", "description": "Inspect live multi-step LangGraph node traces", "shortcut": "T", "command": "open_tab", "payload": {"tab": "traces"}},
    ]
    
    actions = [a for a in default_actions if not query or query in a["title"].lower() or query in a["description"].lower()]
    
    notes_results = []
    if query:
        notes = obsidian_connector.search_notes(query)
        for n in notes[:5]:
            notes_results.append({
                "id": f"note-{n.title}",
                "title": f"📝 {n.title}",
                "category": "vault_note",
                "description": f"Tags: {', '.join(n.tags)} | {n.content[:90]}...",
                "command": "open_note",
                "payload": {"title": n.title}
            })
            
        docs = folder_watcher.list_processed_documents()
        for d in docs:
            if query in d.get("title", "").lower() or query in d.get("summary", "").lower() or query in d.get("filename", "").lower():
                notes_results.append({
                    "id": f"doc-{d.get('filename')}",
                    "title": f"📄 {d.get('title')} ({d.get('doc_type')})",
                    "category": "document",
                    "description": d.get("summary", "")[:110],
                    "command": "open_doc",
                    "payload": d
                })

    ai_suggestions = []
    if query:
        ai_suggestions = [
            {"id": "ai-ask", "title": f"💬 Ask AI: '{q}'", "category": "ai_prompt", "description": "Send natural language instruction to agent engine", "command": "ask_ai", "payload": {"prompt": q}},
            {"id": "ai-res", "title": f"🔬 Deep Research: '{q}'", "category": "ai_prompt", "description": "Deconstruct and research web documentation for this topic", "command": "trigger_research", "payload": {"topic": q}},
        ]

    return {
        "query": q,
        "results": {
            "actions": actions[:6],
            "notes_and_docs": notes_results[:6],
            "ai_prompts": ai_suggestions,
        }
    }


@app.post("/api/rag/ingest_samples")
async def ingest_samples_endpoint():
    """Manually re-indexes all sample files in directives/knowledge_vault/."""
    chunk_count = auto_index_sample_knowledge()
    return {"status": "success", "indexed_chunks": chunk_count}


@app.get("/api/traces")
async def list_traces():
    """List all workflow execution traces for LangSmith-style inspection."""
    return {"traces": [t.model_dump() for t in trace_store.list_traces()]}


@app.get("/api/traces/stats")
async def get_traces_stats():
    """Returns aggregate performance and execution analytics."""
    return {"stats": trace_store.get_stats()}


@app.post("/api/traces/clear")
async def clear_traces_endpoint():
    """Clears all execution traces."""
    trace_store.clear_traces()
    return {"status": "cleared"}


@app.post("/api/traces/simulate")
async def simulate_trace_endpoint(payload: SimulateTracePayload):
    """Generates a rich, realistic multi-step execution trace for testing and demonstration."""
    import uuid
    scenario = payload.scenario or "rag"
    run_id = f"sim-{uuid.uuid4().hex[:8]}"

    if scenario == "calendar_event":
        trace_store.start_trace(run_id=run_id, thread_id="sim-thread", query="Schedule team sync with Alex tomorrow at 3pm", sender="user")
        trace_store.record_node_step(run_id=run_id, node_name="quarantine_node", inputs={"raw_prompt": "Schedule team sync with Alex tomorrow at 3pm"}, outputs={"clean_facts": {"intent": "calendar_create", "summary": "Team sync with Alex", "time": "tomorrow 3pm"}}, duration_ms=42.5, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="triaging_node", inputs={"intent": "calendar_create"}, outputs={"priority_score": 0.88, "category": "important"}, duration_ms=18.2, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="retrieval_node", inputs={"query": "Alex contact calendar"}, outputs={"matches_count": 2, "context": "Alex Johnson (alex@enterprise.com)"}, duration_ms=56.1, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="reasoning_node", inputs={"clean_facts": "...", "retrieved_context": "..."}, outputs={"tool": "calendar.create_event", "rationale": "Scheduling user meeting."}, duration_ms=185.0, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="approval_gate_node", inputs={"tool_name": "calendar.create_event"}, outputs={"status": "AUTO_APPROVED", "tier": "MEDIUM"}, duration_ms=2.1, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="tool_execution_node", inputs={"tool_name": "calendar.create_event", "args": {"summary": "Team sync with Alex", "start_time": "2026-08-29T15:00:00"}}, outputs={"event_id": "ev-88392", "status": "confirmed"}, duration_ms=92.3, status="COMPLETED", tool_call="calendar.create_event", tool_args={"summary": "Team sync with Alex"})
        trace_store.finish_trace(run_id=run_id, status="SUCCESS", planned_tool="calendar.create_event", tool_args={"summary": "Team sync with Alex"}, final_output="✅ Calendar event 'Team sync with Alex' created for tomorrow at 3:00 PM.")

    elif scenario == "high_risk_gate":
        trace_store.start_trace(run_id=run_id, thread_id="sim-thread", query="Send invoice email to accounting@client.com", sender="user")
        trace_store.record_node_step(run_id=run_id, node_name="quarantine_node", inputs={"raw_prompt": "Send invoice email to accounting@client.com"}, outputs={"clean_facts": {"recipient": "accounting@client.com", "subject": "August Invoice"}}, duration_ms=38.0, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="triaging_node", inputs={"intent": "send_email"}, outputs={"priority_score": 0.95}, duration_ms=15.0, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="retrieval_node", inputs={"query": "invoice accounting template"}, outputs={"matches_count": 1}, duration_ms=45.0, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="reasoning_node", inputs={"plan": "Send outbound email"}, outputs={"tool": "email.send"}, duration_ms=190.0, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="approval_gate_node", inputs={"tool_name": "email.send"}, outputs={"status": "PENDING_APPROVAL", "tier": "HIGH"}, duration_ms=3.0, status="GATED")
        trace_store.finish_trace(run_id=run_id, status="AWAITING_APPROVAL", planned_tool="email.send", tool_args={"to": "accounting@client.com", "subject": "August Invoice"}, approval_required=True, final_output="⚠️ Action paused for human approval: email.send")

    else:
        # Default: RAG Retrieval & Knowledge Synthesis
        trace_store.start_trace(run_id=run_id, thread_id="sim-thread", query="Explain Personal AI OS multi-agent architecture and quarantine security", sender="user")
        trace_store.record_node_step(run_id=run_id, node_name="quarantine_node", inputs={"raw_prompt": "Explain Personal AI OS multi-agent architecture"}, outputs={"clean_facts": {"topic": "architecture_security"}}, duration_ms=35.0, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="triaging_node", inputs={"topic": "architecture_security"}, outputs={"priority_score": 0.75, "category": "important"}, duration_ms=12.0, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="retrieval_node", inputs={"query": "Personal AI OS multi-agent quarantine security"}, outputs={"matches_count": 4, "top_score": 0.92, "sources": ["personal_ai_os_guide.txt", "architecture_spec.md"]}, duration_ms=78.5, status="COMPLETED")
        trace_store.record_node_step(run_id=run_id, node_name="reasoning_node", inputs={"retrieved_chunks": 4}, outputs={"tool": "no_action", "synthesis": "Multi-agent LangGraph system with 3-tier isolation."}, duration_ms=210.0, status="COMPLETED")
        trace_store.finish_trace(run_id=run_id, status="SUCCESS", planned_tool=None, final_output="The Personal AI OS utilizes a 3-tier LangGraph multi-agent architecture featuring tool-isolated Dual-LLM quarantine...")

    trace = trace_store.get_trace(run_id)
    return {"status": "simulated", "run_id": run_id, "trace": trace.model_dump() if trace else None}


@app.get("/api/traces/{run_id}")
async def get_trace_detail(run_id: str):
    """Get complete step-by-step node trace for an execution run."""
    trace = trace_store.get_trace(run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {"trace": trace.model_dump()}


# ── Topology DAG Architecture Endpoints ─────────────────────────────────────

@app.get("/api/graph/topology")
async def get_graph_topology():
    """Returns the compiled LangGraph architecture, node metadata, conditional routing rules, and security boundaries."""
    return {
        "graph_name": "Personal AI OS Orchestrator",
        "entry_point": "quarantine_node",
        "exit_points": ["END"],
        "nodes": [
            {
                "id": "quarantine_node",
                "label": "1. Quarantine Node",
                "category": "security",
                "tier": "Tier 1: Security Isolation",
                "color": "cyan",
                "icon": "shield-check",
                "model": "Gemini 2.5 Flash / Fast LLM",
                "isolation": "Tool-Isolated (No file/network/state access)",
                "description": "Sanitizes raw untrusted user/email inputs, neutralizing prompt injection attacks and extracting structured clean facts.",
                "inputs": ["raw_subject", "raw_body", "sender", "is_known_contact"],
                "outputs": ["clean_facts", "is_interactive_command"],
                "typical_latency_ms": 35,
            },
            {
                "id": "triaging_node",
                "label": "2. Triaging Node",
                "category": "classifier",
                "tier": "Tier 1: Fast ML Classification",
                "color": "indigo",
                "icon": "layers",
                "model": "Calibrated Online Logistic Regression + SGD",
                "isolation": "Read-Only Feature Extractor",
                "description": "Calculates importance probability (0.0 to 1.0) and assigns category tag. Routes low-priority noise directly to storage.",
                "inputs": ["clean_facts", "sender"],
                "outputs": ["triage.priority_score", "triage.category", "triage.should_trigger_agent"],
                "typical_latency_ms": 15,
            },
            {
                "id": "retrieval_node",
                "label": "3. Hybrid RAG Node",
                "category": "retrieval",
                "tier": "Tier 2: Knowledge Grounding",
                "color": "emerald",
                "icon": "database",
                "model": "Dense Embedding (MiniLM) + BM25 Lexical + CrossEncoder Reranker",
                "isolation": "Read-Only Vector & Vault Store",
                "description": "Performs Reciprocal Rank Fusion (RRF) across local vector stores, Obsidian notes, and directive guidelines.",
                "inputs": ["clean_facts", "chat_history"],
                "outputs": ["retrieved_context"],
                "typical_latency_ms": 65,
            },
            {
                "id": "low_priority_store_node",
                "label": "2b. Low-Priority Store",
                "category": "storage",
                "tier": "Tier 1: Bypass Storage",
                "color": "slate",
                "icon": "archive",
                "model": "None (Bypass LLM)",
                "isolation": "Database Writer",
                "description": "Archives promotional, spam, or low-priority background messages without consuming LLM reasoning tokens.",
                "inputs": ["clean_facts"],
                "outputs": ["final_output"],
                "typical_latency_ms": 5,
            },
            {
                "id": "reasoning_node",
                "label": "4. ReAct Reasoning Node",
                "category": "reasoning",
                "tier": "Tier 2: Core Cognitive Engine",
                "color": "purple",
                "icon": "brain",
                "model": "Gemini 2.5 Flash / Pro (Structured Output)",
                "isolation": "Planner Sandbox (Emits tool intentions)",
                "description": "Synthesizes retrieved context, evaluates user query intent, constructs reasoning plan, and selects target tool with schema-validated arguments.",
                "inputs": ["clean_facts", "retrieved_context", "chat_history"],
                "outputs": ["plan", "planned_tool", "tool_args", "final_output"],
                "typical_latency_ms": 180,
            },
            {
                "id": "approval_gate_node",
                "label": "5. HITL Safety Gate",
                "category": "security",
                "tier": "Tier 3: Human-in-the-Loop",
                "color": "amber",
                "icon": "alert-triangle",
                "model": "Permission Policy Engine",
                "isolation": "Execution Interceptor",
                "description": "Intercepts High-Risk (Tier 3) tools (e.g. email.send, workspace.write_file) and halts workflow for operator authorization.",
                "inputs": ["planned_tool", "tool_args"],
                "outputs": ["approval_required", "approval_request_id", "approval_status"],
                "typical_latency_ms": 5,
            },
            {
                "id": "tool_execution_node",
                "label": "6. Tool Execution Node",
                "category": "execution",
                "tier": "Tier 3: Action Dispatcher",
                "color": "blue",
                "icon": "cpu",
                "model": "Connector Layer (Gmail, Calendar, Obsidian, Workspace, Web)",
                "isolation": "Sandboxed Tool Connectors",
                "description": "Directly invokes authorized tool connectors with validated arguments and returns formatted result snapshots.",
                "inputs": ["planned_tool", "tool_args"],
                "outputs": ["execution_result", "final_output"],
                "typical_latency_ms": 95,
            },
        ],
        "edges": [
            {"source": "entry_point", "target": "quarantine_node", "type": "direct", "label": "Raw Input"},
            {"source": "quarantine_node", "target": "triaging_node", "type": "direct", "label": "Sanitized Facts"},
            {
                "source": "triaging_node",
                "target": "retrieval_node",
                "type": "conditional",
                "label": "trigger_agent (Score >= 0.5 or Command)",
                "condition": "state.triage.should_trigger_agent == True"
            },
            {
                "source": "triaging_node",
                "target": "low_priority_store_node",
                "type": "conditional",
                "label": "store_low_priority (Score < 0.5)",
                "condition": "state.triage.should_trigger_agent == False"
            },
            {"source": "retrieval_node", "target": "reasoning_node", "type": "direct", "label": "RAG Context"},
            {
                "source": "reasoning_node",
                "target": "approval_gate_node",
                "type": "conditional",
                "label": "execute_tool (Tool Chosen)",
                "condition": "state.planned_tool is not None"
            },
            {
                "source": "reasoning_node",
                "target": "END",
                "type": "conditional",
                "label": "finish (Direct Conversational Answer)",
                "condition": "state.planned_tool is None"
            },
            {
                "source": "approval_gate_node",
                "target": "tool_execution_node",
                "type": "conditional",
                "label": "approved_execute (Auto-Approved / Low-Risk)",
                "condition": "state.approval_required == False"
            },
            {
                "source": "approval_gate_node",
                "target": "END",
                "type": "conditional",
                "label": "awaiting_approval (High-Risk Gated)",
                "condition": "state.approval_required == True"
            },
            {"source": "tool_execution_node", "target": "END", "type": "direct", "label": "Execution Result"},
            {"source": "low_priority_store_node", "target": "END", "type": "direct", "label": "Archived"},
        ]
    }


@app.post("/api/graph/simulate")
async def simulate_graph_execution(payload: SimulateGraphPayload):
    """Simulates an interactive step-by-step traversal across the LangGraph DAG."""
    import uuid
    scenario = payload.scenario or "rag"
    prompt = payload.prompt or ("What is the project architecture and roadmap?" if scenario == "rag" else "Send email to team with update")
    
    run_id = f"sim-{uuid.uuid4().hex[:8]}"
    initial_state = {
        "run_id": run_id,
        "raw_subject": prompt,
        "raw_body": prompt,
        "sender": "user",
        "is_known_contact": True,
        "is_interactive_command": True,
    }
    config = {"configurable": {"thread_id": f"sim-thread-{run_id}"}}
    trace_store.start_trace(query=prompt, thread_id=f"sim-thread-{run_id}", sender="user", run_id=run_id)

    # Run the engine workflow
    t0 = time.perf_counter()
    state = await agent_engine.app.ainvoke(initial_state, config=config)
    total_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "status": "success",
        "scenario": scenario,
        "prompt": prompt,
        "run_id": run_id,
        "total_duration_ms": round(total_ms, 2),
        "state_snapshot": {
            "planned_tool": state.get("planned_tool"),
            "tool_args": state.get("tool_args"),
            "approval_required": state.get("approval_required", False),
            "approval_status": state.get("approval_status"),
            "final_output": state.get("final_output"),
        }
    }




@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time streaming chat with token-by-token LLM output."""
    await ws_manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "Invalid JSON payload."})
                continue

            command = payload.get("command", "").strip()
            if not command:
                await websocket.send_json({"type": "error", "content": "Empty command."})
                continue

            # Signal thinking start
            await websocket.send_json({"type": "thinking", "content": "⚙️ Executing LangGraph DAG..."})

            session_id = payload.get("session_id") or f"session-{uuid.uuid4().hex[:8]}"
            thread_id = payload.get("thread_id") or session_id
            config = {"configurable": {"thread_id": thread_id}}

            # Retrieve prior conversation turns for stateful multi-turn reasoning
            past_messages = chat_history_store.get_session_messages(session_id)
            history_tuples = [{"role": m.role, "content": m.content} for m in past_messages[-10:]]

            # Record user message in local SQLite history
            chat_history_store.add_message(session_id=session_id, role="user", content=command)

            trace = trace_store.start_trace(query=command, thread_id=thread_id, sender="user")

            initial_state = {
                "run_id": trace.run_id,
                "raw_subject": "User Command",
                "raw_body": command,
                "sender": "user",
                "is_known_contact": True,
                "is_interactive_command": True,
                "chat_history": history_tuples,
            }

            try:
                result = await agent_engine.app.ainvoke(initial_state, config=config)
                pipeline_output = result.get("final_output", "Done.")
                planned_tool = result.get("planned_tool")
                tool_args = result.get("tool_args")
                approval_required = result.get("approval_required", False)
                approval_request_id = result.get("approval_request_id")

                trace_store.complete_trace(
                    run_id=trace.run_id,
                    status="AWAITING_APPROVAL" if approval_required else "SUCCESS",
                    final_output=pipeline_output,
                    planned_tool=planned_tool,
                    tool_args=tool_args,
                    approval_required=approval_required,
                    approval_request_id=approval_request_id,
                )

                # Record assistant response in local SQLite history
                chat_history_store.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=pipeline_output,
                    run_id=trace.run_id,
                    planned_tool=planned_tool,
                    tool_args=tool_args,
                    approval_required=approval_required,
                    approval_request_id=approval_request_id,
                )

                # Continuously ingest conversation Q&A into hybrid vector RAG store
                try:
                    qa_summary = f"User Query: {command}\nPersonal AI Response: {pipeline_output}"
                    if planned_tool and planned_tool != "no_action":
                        qa_summary += f"\nAction Performed: {planned_tool} with parameters {tool_args}"
                    vector_store.insert_chunks([
                        DocumentChunk(
                            text=qa_summary,
                            source_type="chat_interaction",
                            metadata={
                                "session_id": session_id,
                                "run_id": trace.run_id,
                                "timestamp": time.time(),
                                "query": command,
                            },
                        )
                    ])
                except Exception:
                    pass
            except Exception as exc:
                trace_store.complete_trace(run_id=trace.run_id, status="ERROR", error=str(exc))
                chat_history_store.add_message(session_id=session_id, role="assistant", content=f"⚠️ Error: {str(exc)}")
                await websocket.send_json({"type": "error", "content": str(exc), "session_id": session_id})
                continue

            # Send final pipeline result
            await websocket.send_json({
                "type": "done",
                "content": pipeline_output,
                "planned_tool": planned_tool,
                "tool_args": tool_args,
                "approval_required": approval_required,
                "approval_request_id": approval_request_id,
                "thread_id": thread_id,
                "session_id": session_id,
                "run_id": trace.run_id,
            })

    except WebSocketDisconnect:
        pass


from server.dashboard_template import DASHBOARD_HTML


@app.get("/manifest.json")
async def get_manifest():
    """PWA Web App Manifest for Desktop App installation."""
    return {
        "name": "Personal AI OS — Command Center",
        "short_name": "Personal AI OS",
        "description": "Local-first Personal AI Command Center and Automation Engine",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#07080d",
        "theme_color": "#6366f1",
        "orientation": "any",
        "icons": [
            {
                "src": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/cpu.svg",
                "sizes": "192x192 512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    }


# Web Command Center Dashboard UI
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the rich, responsive Personal AI OS Web Command Center with Omarchy ricing themes and live wallpapers."""
    return HTMLResponse(content=DASHBOARD_HTML)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('server.app:app', host=settings.API_HOST, port=settings.API_PORT, reload=False)
