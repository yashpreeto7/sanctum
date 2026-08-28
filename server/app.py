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

# In-memory inbox store for dashboard display
inbox_store: List[Dict[str, Any]] = []

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


class FeedbackPayload(BaseModel):
    text: str
    user_label: int = Field(..., description="1 = Important, 0 = Unimportant")



# API Endpoints
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
        inbox_emails = gmail_connector.list_inbox_messages(max_results=35)
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

        return {"status": "synced", "total_inbox": len(inbox_store), "new_synced": new_count}
    except Exception as e:
        return {"status": "error", "error": str(e), "total_inbox": len(inbox_store)}


@app.get("/api/inbox")
async def list_inbox():
    """Retrieve all triaged inbound messages, auto-syncing live Gmail if empty."""
    if not inbox_store:
        try:
            await sync_live_gmail()
        except Exception:
            pass
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


@app.get("/api/calendar/events")
async def list_calendar_events(
    days_back: int = 120,
    days_ahead: int = 365,
    include_festivals: bool = True,
):
    """Lists calendar events and cultural festivals across past, present, and future ranges."""
    try:
        events = calendar_connector.list_upcoming_events(
            days_back=days_back,
            days_ahead=days_ahead,
            include_festivals=include_festivals,
        )
        return {"status": "success", "events": [e.model_dump() for e in events]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {str(e)}")


@app.get("/api/calendar/festivals")
async def list_festivals(year: Optional[int] = None):
    """Returns curated cultural and public festivals for a year."""
    try:
        festivals = calendar_connector.list_festivals(year=year)
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
        res = calendar_connector.create_event(ev)
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@app.delete("/api/calendar/event")
async def delete_calendar_event(event_id: str):
    """Deletes a calendar event by ID."""
    try:
        deleted = calendar_connector.delete_event(event_id=event_id)
        return {"status": "success", "deleted": deleted, "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")


# ── Obsidian Vault Endpoints ──

@app.get("/api/obsidian/status")
async def get_obsidian_status():
    """Returns Obsidian vault connection status, location path, and note stats."""
    vault_path = obsidian_connector.vault_path
    notes = obsidian_connector.list_all_notes()
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
    notes = obsidian_connector.list_all_notes()
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


@app.post("/api/approvals/{request_id}/resolve")
async def resolve_approval(request_id: str, payload: ResolveApprovalPayload):
    """Approve or reject a pending high-risk tool execution."""
    resolved = permission_manager.resolve_request(request_id, approved=payload.approved)
    if not resolved:
        raise HTTPException(status_code=404, detail="Approval request not found")

    execution_output = None
    if payload.approved:
        # Execute the tool directly now that human authorization is granted
        _, output_msg = agent_engine.execute_tool_directly(resolved.tool_name, resolved.tool_args)
        execution_output = output_msg

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
    """Uploads a document (PDF, TXT, MD, JSON), extracts text, chunks, and indexes it into the vector store."""
    filename = file.filename or "uploaded_doc.txt"
    content_bytes = await file.read()

    extracted_text = ""
    if filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            pdf_file = io.BytesIO(content_bytes)
            reader = PdfReader(pdf_file)
            extracted_text = "\n\n".join([page.extract_text() or "" for page in reader.pages])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
    else:
        try:
            extracted_text = content_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to decode text: {str(e)}")

    extracted_text = extracted_text.strip()
    if not extracted_text:
        raise HTTPException(status_code=400, detail="Uploaded file contains no readable text.")

    # Save to knowledge vault
    KNOWLEDGE_VAULT_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = KNOWLEDGE_VAULT_DIR / filename
    saved_path.write_bytes(content_bytes)

    # Split text into chunks
    sections = [s.strip() for s in extracted_text.split("\n\n") if s.strip()]
    chunks: List[DocumentChunk] = []
    curr_block = ""
    for sec in sections:
        if len(curr_block) + len(sec) < 500:
            curr_block += "\n\n" + sec if curr_block else sec
        else:
            if curr_block:
                chunks.append(DocumentChunk(
                    text=curr_block.strip(),
                    source_type=f"upload:{filename}",
                    metadata={"filename": filename, "source": "user_upload", "timestamp": time.time()}
                ))
            curr_block = sec
    if curr_block:
        chunks.append(DocumentChunk(
            text=curr_block.strip(),
            source_type=f"upload:{filename}",
            metadata={"filename": filename, "source": "user_upload", "timestamp": time.time()}
        ))

    if chunks:
        vector_store.insert_chunks(chunks)

    return {
        "status": "success",
        "filename": filename,
        "total_chars": len(extracted_text),
        "chunks_indexed": len(chunks),
        "preview": extracted_text[:300] + ("..." if len(extracted_text) > 300 else "")
    }


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
    await asyncio.sleep(4)
    while True:
        try:
            from execution.tools.gmail_connector import gmail_connector
            recent = gmail_connector.list_inbox_messages(max_results=15)
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
        await asyncio.sleep(10)


@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(proactive_background_worker())


@app.post("/api/rag/ingest_samples")
async def ingest_samples_endpoint():
    """Manually re-indexes all sample files in directives/knowledge_vault/."""
    chunk_count = auto_index_sample_knowledge()
    return {"status": "success", "indexed_chunks": chunk_count}


@app.get("/api/traces")
async def list_traces():
    """List all workflow execution traces for LangSmith-style inspection."""
    return {"traces": [t.model_dump() for t in trace_store.list_traces()]}


@app.get("/api/traces/{run_id}")
async def get_trace_detail(run_id: str):
    """Get complete step-by-step node trace for an execution run."""
    trace = trace_store.get_trace(run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {"trace": trace.model_dump()}


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
