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
    execution_result: Optional[str] = None
    operator_notes: Optional[str] = None



class PermissionManager:
    """Enforces safety policies, manages pending approval queue, and maintains an audit log."""

    # Default tool registry risk classifications
    TOOL_RISK_MAP: Dict[str, RiskLevel] = {
        "obsidian.create_note": RiskLevel.LOW,
        "obsidian.append_daily_log": RiskLevel.LOW,
        "obsidian.search_notes": RiskLevel.LOW,
        "rag.search": RiskLevel.LOW,
        "web.search": RiskLevel.LOW,
        "workspace.list_files": RiskLevel.LOW,
        "workspace.read_file": RiskLevel.LOW,
        "workspace.write_file": RiskLevel.HIGH,
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
        self._history: List[ApprovalRequest] = []
        self._require_high_risk: bool = True
        self._auto_approve_low_risk: bool = True
        self._auto_approve_medium_risk: bool = False

    def get_tool_risk(self, tool_name: str) -> RiskLevel:
        """Look up the risk level for a tool."""
        return self.TOOL_RISK_MAP.get(tool_name, RiskLevel.HIGH)

    def can_auto_execute(self, tool_name: str) -> bool:
        """Determines if a tool call can proceed without prompting the user."""
        risk = self.get_tool_risk(tool_name)
        if risk == RiskLevel.LOW and self._auto_approve_low_risk:
            return True
        if risk == RiskLevel.MEDIUM and self._auto_approve_medium_risk:
            return True
        if not self._require_high_risk and risk == RiskLevel.HIGH:
            return True
        return False

    def get_policies(self) -> Dict[str, Any]:
        """Returns current safety policy settings and risk mapping."""
        return {
            "require_high_risk": self._require_high_risk,
            "auto_approve_low_risk": self._auto_approve_low_risk,
            "auto_approve_medium_risk": self._auto_approve_medium_risk,
            "tool_risk_map": {k: v.value for k, v in self.TOOL_RISK_MAP.items()},
        }

    def update_policies(self, policies: Dict[str, Any]) -> Dict[str, Any]:
        """Updates active security policies."""
        if "require_high_risk" in policies:
            self._require_high_risk = bool(policies["require_high_risk"])
        if "auto_approve_low_risk" in policies:
            self._auto_approve_low_risk = bool(policies["auto_approve_low_risk"])
        if "auto_approve_medium_risk" in policies:
            self._auto_approve_medium_risk = bool(policies["auto_approve_medium_risk"])
        return self.get_policies()

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

    def resolve_request(
        self,
        request_id: str,
        approved: bool,
        edited_args: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        execution_result: Optional[str] = None,
    ) -> Optional[ApprovalRequest]:
        """User approves or rejects a pending action in the UI."""
        if request_id not in self._approval_queue:
            return None

        req = self._approval_queue[request_id]
        if edited_args:
            req.tool_args = edited_args
        req.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        req.resolved_at = time.time()
        if notes:
            req.operator_notes = notes
        if execution_result:
            req.execution_result = execution_result

        # Move from active queue to history
        self._history.insert(0, req)
        if len(self._history) > 100:
            self._history.pop()

        return req

    def list_pending_requests(self) -> List[ApprovalRequest]:
        """Returns all approval requests currently awaiting human input."""
        return [r for r in self._approval_queue.values() if r.status == ApprovalStatus.PENDING]

    def list_history(self, limit: int = 50) -> List[ApprovalRequest]:
        """Returns past resolved approvals for the audit log."""
        return self._history[:limit]

    def clear_history(self) -> None:
        """Clears audit history log."""
        self._history.clear()


# Singleton instance
permission_manager = PermissionManager()

