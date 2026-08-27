"""3-Tier Risk Permission Manager and Human-In-The-Loop (HITL) Gatekeeper."""

import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from execution.core.config import settings


class RiskLevel(str, Enum):
    """Categorization of tool execution risk."""

    LOW = "LOW"        # Read-only, private note creation, semantic search -> Auto-approved
    MEDIUM = "MEDIUM"  # Calendar creation, email drafting, updating notes -> Configurable
    HIGH = "HIGH"      # Sending external emails, deleting items, executing shell -> Explicit Approval Required


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalRequest(BaseModel):
    """Container for a pending human approval card."""

    id: str = Field(default_factory=lambda: f"req-{uuid.uuid4().hex[:8]}")
    tool_name: str
    tool_args: Dict[str, Any]
    risk_level: RiskLevel
    human_readable_summary: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = Field(default_factory=time.time)
    resolved_at: Optional[float] = None


class PermissionManager:
    """Enforces safety policies and manages the pending approval queue."""

    # Default tool registry risk classifications
    TOOL_RISK_MAP: Dict[str, RiskLevel] = {
        "obsidian.create_note": RiskLevel.LOW,
        "obsidian.append_daily_log": RiskLevel.LOW,
        "obsidian.search_notes": RiskLevel.LOW,
        "rag.search": RiskLevel.LOW,
        "calendar.list_events": RiskLevel.LOW,
        "calendar.create_event": RiskLevel.MEDIUM,
        "email.list_unread": RiskLevel.LOW,
        "email.search": RiskLevel.LOW,
        "email.get_email": RiskLevel.LOW,
        "email.create_draft": RiskLevel.MEDIUM,
        "email.send": RiskLevel.HIGH,
        "shell.execute": RiskLevel.HIGH,
    }

    def __init__(self):
        self._approval_queue: Dict[str, ApprovalRequest] = {}

    def get_tool_risk(self, tool_name: str) -> RiskLevel:
        """Look up the risk level for a tool."""
        return self.TOOL_RISK_MAP.get(tool_name, RiskLevel.HIGH)

    def can_auto_execute(self, tool_name: str) -> bool:
        """Determines if a tool call can proceed without prompting the user."""
        if not settings.REQUIRE_APPROVAL_FOR_HIGH_RISK:
            return True
        risk = self.get_tool_risk(tool_name)
        if risk == RiskLevel.LOW and settings.AUTO_APPROVE_LOW_RISK:
            return True
        return False

    def create_approval_request(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        summary: Optional[str] = None,
    ) -> ApprovalRequest:
        """Creates and registers an approval request waiting for human resolution."""
        risk = self.get_tool_risk(tool_name)
        readable = summary or f"Execute '{tool_name}' with arguments: {tool_args}"

        request = ApprovalRequest(
            tool_name=tool_name,
            tool_args=tool_args,
            risk_level=risk,
            human_readable_summary=readable,
            status=ApprovalStatus.PENDING,
        )
        self._approval_queue[request.id] = request
        return request

    def resolve_request(self, request_id: str, approved: bool) -> Optional[ApprovalRequest]:
        """User approves or rejects a pending action in the UI."""
        if request_id not in self._approval_queue:
            return None

        req = self._approval_queue[request_id]
        req.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        req.resolved_at = time.time()
        return req

    def list_pending_requests(self) -> List[ApprovalRequest]:
        """Returns all approval requests currently awaiting human input."""
        return [r for r in self._approval_queue.values() if r.status == ApprovalStatus.PENDING]


# Singleton instance
permission_manager = PermissionManager()
