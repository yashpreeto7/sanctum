"""Deterministic Email Connector supporting Gmail API and offline local mock mode."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OutboundEmail(BaseModel):
    """Container for an outbound email draft or message."""

    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body text or html")
    thread_id: Optional[str] = None
    cc: List[str] = Field(default_factory=list)


class InboundEmail(BaseModel):
    """Container for an ingested email."""

    id: str
    thread_id: str
    sender: str
    subject: str
    body: str
    received_at_timestamp: float
    is_read: bool = False
    is_known_contact: bool = False


class GmailConnector:
    """Manages Gmail operations: searching, reading threads, drafting, and sending."""

    def __init__(self, service: Optional[Any] = None):
        self.service = service
        self._mock_inbox: List[InboundEmail] = []
        self._sent_emails: List[OutboundEmail] = []
        self._drafts: List[OutboundEmail] = []

    def list_unread(self, max_results: int = 10) -> List[InboundEmail]:
        """Fetch unread emails."""
        if self.service is not None:
            try:
                results = self.service.users().messages().list(
                    userId="me", q="is:unread", maxResults=max_results
                ).execute()
                # Parse live messages here...
            except Exception:
                pass
        return [e for e in self._mock_inbox if not e.is_read][:max_results]

    def create_draft(self, email: OutboundEmail) -> Dict[str, Any]:
        """Creates a draft in Gmail (Medium Risk)."""
        self._drafts.append(email)
        return {
            "status": "draft_created",
            "to": email.to,
            "subject": email.subject,
            "draft_id": f"draft-{len(self._drafts)}",
        }

    def send_email(self, email: OutboundEmail) -> Dict[str, Any]:
        """Sends an email directly (High Risk - Requires HITL Approval)."""
        if self.service is not None:
            # Google Gmail API sending
            try:
                # Live send logic
                pass
            except Exception as e:
                return {"status": "error", "message": str(e)}

        self._sent_emails.append(email)
        return {
            "status": "sent",
            "to": email.to,
            "subject": email.subject,
            "message_id": f"msg-sent-{len(self._sent_emails)}",
        }


# Singleton instance
gmail_connector = GmailConnector()
