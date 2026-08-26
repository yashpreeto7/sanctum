# Directive: Stateful LangGraph Orchestration & HITL Safety Protocol

## Goal
Manage stateful multi-step agent workflows with resilient state checkpointing, deterministic tool execution, and zero unauthorized high-risk operations.

## LangGraph State Machine Architecture

```mermaid
stateDiagram-v2
    [*] --> QuarantineNode: Inbound Event
    QuarantineNode --> TriagingNode: Sanitized Facts
    
    state TriagingDecision <<choice>>
    TriagingNode --> TriagingDecision: Evaluate Score
    TriagingDecision --> LowPriorityStoreNode: Score < 0.5
    TriagingDecision --> RetrievalNode: Score >= 0.5
    
    LowPriorityStoreNode --> [*]: Log & Finish (0 LLM Cost)
    RetrievalNode --> ReasoningNode: Ingest Top 3 RAG Chunks
    
    state ApprovalCheck <<choice>>
    ReasoningNode --> ApprovalGateNode: Planned Tool Action
    ApprovalGateNode --> ApprovalCheck: Check Risk Level
    
    ApprovalCheck --> ToolExecutionNode: Low Risk (Auto-Approved)
    ApprovalCheck --> CheckpointedPause: High Risk (Pending User Approval)
    
    CheckpointedPause --> ToolExecutionNode: User Approves in UI
    ToolExecutionNode --> [*]: Success Output
```

## Tool Risk Taxonomy
| Tool Name | Risk Level | Execution Policy |
| :--- | :--- | :--- |
| `obsidian.create_note` | **LOW** | Auto-execute |
| `obsidian.append_daily_log` | **LOW** | Auto-execute |
| `obsidian.search_notes` | **LOW** | Auto-execute |
| `rag.search` | **LOW** | Auto-execute |
| `calendar.list_events` | **LOW** | Auto-execute |
| `calendar.create_event` | **MEDIUM** | Auto-execute / Notify in UI |
| `email.create_draft` | **MEDIUM** | Auto-execute / Notify in UI |
| `email.send` | **HIGH** | **Explicit Approval Required** |
| `shell.execute` | **HIGH** | **Explicit Approval Required** |

## Resuming Checkpointed Workflows
When an agent hits a high-risk tool (`email.send`), LangGraph snapshots the execution state to the checkpointer and returns `PENDING`.
When the user approves via API/UI (`POST /api/approvals/{id}/resolve`):
1. `permission_manager.resolve_request(id, approved=True)`
2. The engine resumes the saved thread checkpoint directly at `tool_execution_node` without re-running prior LLM steps.
