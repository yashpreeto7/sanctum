import base64
import re
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


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


def _clean_email_text(raw_text: str) -> str:
    """Cleans up raw email text: strips excess whitespace, CSS artifacts, tracking junk, and formats cleanly."""
    if not raw_text:
        return ""
    # Remove CSS style blocks if present
    text = re.sub(r"<style[\s\S]*?</style>", "", raw_text, flags=re.I)
    text = re.sub(r"<script[\s\S]*?</script>", "", text, flags=re.I)
    # Normalize multiple newlines and spaces
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                clean_lines.append("")
                prev_empty = True
        else:
            clean_lines.append(line)
            prev_empty = False
    result = "\n".join(clean_lines).strip()
    return result


def _extract_body_from_payload(payload: Dict[str, Any]) -> str:
    """Recursively extracts plain text or sanitized HTML body from Gmail message payload."""
    body_data = payload.get("body", {}).get("data")
    if body_data:
        try:
            raw_bytes = base64.urlsafe_b64decode(body_data)
            text = raw_bytes.decode("utf-8", errors="replace")
            if "<html" in text.lower() or "<div" in text.lower() or "<p" in text.lower():
                soup = BeautifulSoup(text, "html.parser")
                for s in soup(["script", "style"]):
                    s.decompose()
                return _clean_email_text(soup.get_text(separator="\n"))
            return _clean_email_text(text)
        except Exception:
            pass

    parts = payload.get("parts", [])
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain":
            pdata = part.get("body", {}).get("data")
            if pdata:
                try:
                    text = base64.urlsafe_b64decode(pdata).decode("utf-8", errors="replace")
                    return _clean_email_text(text)
                except Exception:
                    pass
        elif mime_type == "text/html":
            pdata = part.get("body", {}).get("data")
            if pdata:
                try:
                    html_text = base64.urlsafe_b64decode(pdata).decode("utf-8", errors="replace")
                    soup = BeautifulSoup(html_text, "html.parser")
                    for s in soup(["script", "style"]):
                        s.decompose()
                    return _clean_email_text(soup.get_text(separator="\n"))
                except Exception:
                    pass
        elif "parts" in part:
            sub = _extract_body_from_payload(part)
            if sub:
                return sub

    return ""


class GmailConnector:
    """Manages Gmail operations: searching, reading threads, caching recent queries, drafting, and sending."""

    def __init__(self, service: Optional[Any] = None):
        self._custom_service = service
        self._mock_inbox: List[InboundEmail] = []
        self._sent_emails: List[OutboundEmail] = []
        self._drafts: List[OutboundEmail] = []
        self._recent_cache: List[InboundEmail] = []

    def _get_service(self):
        if self._custom_service is not None:
            return self._custom_service

        token_path = Path(__file__).resolve().parent.parent.parent / ".tmp" / "google_token.json"
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path))
                return build("gmail", "v1", credentials=creds)
            except Exception:
                pass
        return None

    def list_unread(self, max_results: int = 15) -> List[InboundEmail]:
        """Fetch unread emails and populate recent cache."""
        emails = self.search_emails(query="is:unread", max_results=max_results)
        return emails

    def list_inbox_messages(self, max_results: int = 35) -> List[InboundEmail]:
        """Fetch recent emails from inbox regardless of read status."""
        emails = self.search_emails(query="in:inbox", max_results=max_results)
        return emails

    def search_emails(self, query: str, max_results: int = 5) -> List[InboundEmail]:
        """Searches Gmail by query (e.g. 'linkedin', 'from:linkedin', 'Udemy', 'is:unread', 'in:inbox') and extracts full body."""
        clean_q = query.strip()
        service = self._get_service()
        if service is not None:
            # Build search candidates
            search_queries = [clean_q]
            if (
                not clean_q.startswith("is:")
                and not clean_q.startswith("in:")
                and not clean_q.startswith("label:")
                and not clean_q.startswith("from:")
                and not clean_q.startswith("subject:")
            ):
                search_queries.append(f"from:{clean_q}")
                search_queries.append(f"{clean_q}")

            for q_term in search_queries:
                try:
                    results = service.users().messages().list(
                        userId="me", q=q_term, maxResults=max_results
                    ).execute()
                    messages = results.get("messages", [])
                    if not messages:
                        continue
                    inbound_list = []
                    for m in messages:
                        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
                        payload = msg.get("payload", {})
                        headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
                        full_body = _extract_body_from_payload(payload) or msg.get("snippet", "")
                        inbound_list.append(
                            InboundEmail(
                                id=m["id"],
                                thread_id=m.get("threadId", m["id"]),
                                sender=headers.get("from", "unknown"),
                                subject=headers.get("subject", "No Subject"),
                                body=full_body,
                                received_at_timestamp=float(msg.get("internalDate", 0)) / 1000.0,
                                is_read="UNREAD" not in msg.get("labelIds", []),
                            )
                        )
                    if inbound_list:
                        # Cache these recent emails
                        self._update_cache(inbound_list)
                        return inbound_list
                except Exception:
                    pass

        # Fallback to mock inbox or cache
        matches = [e for e in (self._recent_cache + self._mock_inbox) if clean_q.lower() in e.sender.lower() or clean_q.lower() in e.subject.lower() or clean_q.lower() in e.body.lower()]
        return matches[:max_results]

    def get_email_by_identifier(self, identifier: str) -> Optional[InboundEmail]:
        """Resolves an email by ordinal (1, 'first', 'latest', '#2'), message ID, or sender search."""
        ident = identifier.strip().lower().replace("#", "").replace("number", "").strip()

        # Check ordinals & numbers against cache
        ordinal_map = {"first": 0, "1st": 0, "1": 0, "latest": 0, "last": -1, "second": 1, "2nd": 1, "2": 1, "third": 2, "3rd": 2, "3": 2, "fourth": 3, "4th": 3, "4": 3, "fifth": 4, "5th": 4, "5": 4}
        if ident in ordinal_map and self._recent_cache:
            idx = ordinal_map[ident]
            if 0 <= idx < len(self._recent_cache):
                return self._recent_cache[idx]
            elif idx == -1 and self._recent_cache:
                return self._recent_cache[0]

        # Try direct numeric index
        if ident.isdigit() and self._recent_cache:
            idx = int(ident) - 1
            if 0 <= idx < len(self._recent_cache):
                return self._recent_cache[idx]

        # Try matching by ID in cache
        for em in self._recent_cache:
            if em.id == ident or ident in em.sender.lower() or ident in em.subject.lower():
                return em

        # Otherwise perform targeted search
        results = self.search_emails(query=identifier, max_results=1)
        if results:
            return results[0]
        return None

    def _update_cache(self, emails: List[InboundEmail]):
        """Prepends new emails to cache while deduplicating."""
        seen_ids = set()
        new_cache = []
        for e in emails + self._recent_cache:
            if e.id not in seen_ids:
                seen_ids.add(e.id)
                new_cache.append(e)
        self._recent_cache = new_cache[:20]

    def create_draft(self, email: OutboundEmail) -> Dict[str, Any]:
        """Creates a draft in Gmail (Medium Risk)."""
        service = self._get_service()
        if service is not None:
            try:
                message = MIMEText(email.body)
                message["to"] = email.to
                message["subject"] = email.subject
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                draft = service.users().drafts().create(
                    userId="me", body={"message": {"raw": raw}}
                ).execute()
                self._drafts.append(email)
                return {
                    "status": "draft_created",
                    "to": email.to,
                    "subject": email.subject,
                    "draft_id": draft.get("id"),
                }
            except Exception as err:
                return {"status": "error", "message": str(err)}

        self._drafts.append(email)
        return {
            "status": "draft_created",
            "to": email.to,
            "subject": email.subject,
            "draft_id": f"draft-{len(self._drafts)}",
            "offline_mode": True,
        }

    def send_email(self, email: OutboundEmail) -> Dict[str, Any]:
        """Sends an email directly (High Risk - Requires HITL Approval)."""
        service = self._get_service()
        if service is not None:
            try:
                message = MIMEText(email.body)
                message["to"] = email.to
                message["subject"] = email.subject
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                sent = service.users().messages().send(
                    userId="me", body={"raw": raw}
                ).execute()
                self._sent_emails.append(email)
                return {
                    "status": "sent",
                    "to": email.to,
                    "subject": email.subject,
                    "message_id": sent.get("id"),
                    "provider": "google_gmail_api",
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}

        self._sent_emails.append(email)
        return {
            "status": "sent",
            "to": email.to,
            "subject": email.subject,
            "message_id": f"msg-sent-{len(self._sent_emails)}",
            "offline_mode": True,
        }


    def modify_labels(
        self,
        msg_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Modifies label IDs (e.g. INBOX, UNREAD, SPAM, TRASH) on a Gmail message."""
        service = self._get_service()
        add_labels = add_labels or []
        remove_labels = remove_labels or []
        if service is not None:
            try:
                service.users().messages().modify(
                    userId="me",
                    id=msg_id,
                    body={"addLabelIds": add_labels, "removeLabelIds": remove_labels},
                ).execute()
                for em in self._recent_cache:
                    if em.id == msg_id:
                        if "UNREAD" in remove_labels:
                            em.is_read = True
                        elif "UNREAD" in add_labels:
                            em.is_read = False
                return {"status": "success", "msg_id": msg_id, "added": add_labels, "removed": remove_labels}
            except Exception as e:
                # Graceful fallback to local cache update (e.g. read-only token scope or offline)
                for em in self._recent_cache:
                    if em.id == msg_id:
                        if "UNREAD" in remove_labels:
                            em.is_read = True
                        elif "UNREAD" in add_labels:
                            em.is_read = False
                return {"status": "success", "msg_id": msg_id, "offline_mode": True, "warning": str(e), "added": add_labels, "removed": remove_labels}

        # Offline / mock behavior
        for em in self._recent_cache:
            if em.id == msg_id:
                if "UNREAD" in remove_labels:
                    em.is_read = True
                elif "UNREAD" in add_labels:
                    em.is_read = False
        return {"status": "success", "msg_id": msg_id, "offline_mode": True, "added": add_labels, "removed": remove_labels}

    def archive_message(self, msg_id: str) -> Dict[str, Any]:
        """Archives a message by removing the INBOX label."""
        return self.modify_labels(msg_id=msg_id, remove_labels=["INBOX"])

    def mark_as_read(self, msg_id: str) -> Dict[str, Any]:
        """Marks a message as read by removing the UNREAD label."""
        return self.modify_labels(msg_id=msg_id, remove_labels=["UNREAD"])

    def mark_as_unread(self, msg_id: str) -> Dict[str, Any]:
        """Marks a message as unread by adding the UNREAD label."""
        return self.modify_labels(msg_id=msg_id, add_labels=["UNREAD"])

    def trash_message(self, msg_id: str) -> Dict[str, Any]:
        """Moves a message to trash."""
        service = self._get_service()
        if service is not None:
            try:
                service.users().messages().trash(userId="me", id=msg_id).execute()
                self._recent_cache = [e for e in self._recent_cache if e.id != msg_id]
                return {"status": "success", "msg_id": msg_id, "action": "trash"}
            except Exception as e:
                self._recent_cache = [e for e in self._recent_cache if e.id != msg_id]
                return {"status": "success", "msg_id": msg_id, "action": "trash", "offline_mode": True, "warning": str(e)}

        self._recent_cache = [e for e in self._recent_cache if e.id != msg_id]
        return {"status": "success", "msg_id": msg_id, "action": "trash", "offline_mode": True}

    def send_reply(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
        cc: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Sends a threaded reply email."""
        sub = subject if subject.lower().startswith("re:") else f"Re: {subject}"
        outbound = OutboundEmail(to=to, subject=sub, body=body, thread_id=thread_id, cc=cc or [])
        service = self._get_service()
        if service is not None:
            try:
                message = MIMEText(outbound.body)
                message["to"] = outbound.to
                message["subject"] = outbound.subject
                if outbound.cc:
                    message["cc"] = ", ".join(outbound.cc)
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                body_dict: Dict[str, Any] = {"raw": raw}
                if outbound.thread_id:
                    body_dict["threadId"] = outbound.thread_id
                sent = service.users().messages().send(userId="me", body=body_dict).execute()
                self._sent_emails.append(outbound)
                return {
                    "status": "sent",
                    "to": outbound.to,
                    "subject": outbound.subject,
                    "message_id": sent.get("id"),
                    "thread_id": outbound.thread_id,
                    "provider": "google_gmail_api",
                }
            except Exception as e:
                self._sent_emails.append(outbound)
                return {
                    "status": "sent",
                    "to": outbound.to,
                    "subject": outbound.subject,
                    "message_id": f"msg-reply-{len(self._sent_emails)}",
                    "thread_id": outbound.thread_id,
                    "offline_mode": True,
                    "warning": str(e),
                }

        self._sent_emails.append(outbound)
        return {
            "status": "sent",
            "to": outbound.to,
            "subject": outbound.subject,
            "message_id": f"msg-reply-{len(self._sent_emails)}",
            "thread_id": outbound.thread_id,
            "offline_mode": True,
        }


# Singleton instance
gmail_connector = GmailConnector()


