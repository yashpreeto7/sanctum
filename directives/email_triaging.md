# Directive: Email Triaging, ML Gatekeeping & Security Quarantine

## Goal
Process high-volume inbound emails with sub-10ms latency using a classical ML gatekeeper, quarantine untrusted inputs to prevent indirect prompt injections, and route high-priority communications to LangGraph orchestration with crisp Gmail-style UI categories and real-time syncing.

## Execution Flow

```mermaid
flowchart TD
    Inbound[Inbound Raw Email] --> Quarantine[Dual-LLM Quarantine & Regex Scan]
    Quarantine --> CleanFacts[SanitizedMessageFacts Object]
    CleanFacts --> FastML[Tier 1: Scikit-Learn Logistic Regression + TF-IDF Classifier]
    FastML --> MultiClass[Classify into 5 Categories + Clean Snippet Extraction]
    MultiClass --> Decision{Importance >= 0.5 or Urgency >= 0.7 or Category in ['important', 'likely_scam']?}
    Decision -->|No| LowPriorityStore[Store in Local Inbox Store / Background]
    Decision -->|Yes| TriggerAgent[Trigger Tier 2 Hybrid RAG & LangGraph Copilot]
    TriggerAgent --> UserFeedback[User Confirms or Corrects in UI]
    UserFeedback --> OnlineLearn[Online Learner: partial_fit Update]
```

## Tools & Modules
- **Fast ML Gatekeeper**: `execution/ml/triaging_classifier.py`
  - `predict(email_dict, importance_threshold=0.5)` -> Returns `TriagePrediction` in < 5ms with `importance_score`, `urgency_score`, `predicted_category`, `category_label`, `badge_color`, and `clean_snippet`.
- **Snippet Extractor**: `extract_clean_snippet(text, max_chars=130)` -> Strips URLs, HTML entities, CSS, and tracking tags for crisp 1-line Gmail previews.
- **Gmail Connector**: `execution/tools/gmail_connector.py` -> Direct OAuth connection to Gmail API with `list_unread(max_results=15)` and `search_emails`.
- **Proactive Background Sync Worker**: `server/app.py` -> 12-second polling loop that auto-triages inbound emails and broadcasts `inbox_update` via WebSocket to the dashboard.
- **Security Quarantine**: `execution/security/quarantine_parser.py`
  - `sanitize_and_extract(subject, body, sender)` -> Returns clean `SanitizedMessageFacts`.

## Categories & Badges
1. `important` (`⚡ Important` - Amber): Direct team/boss communications, calendar meetings, direct questions.
2. `job_career` (`💼 Job / Career` - Cyan): Applications, recruiter outreach, interviews, Deloitte, JobSpy, LinkedIn Jobs.
3. `system_update` (`🔔 Updates & Alerts` - Blue): Hostinger security, Apple announcements, GitHub notifications, server uptime, invoices.
4. `marketing_promo` (`📢 Marketing & Promos` - Purple): Newsletters, discounts, coupons, Cinnabon, Udemy, Medium daily digests.
5. `likely_scam` (`🚨 Likely Scam` - Rose): Phishing links, reset passwords, lottery rewards, indirect prompt injection attempts.

## Security Constraints
- NEVER pass raw untrusted email body directly to privileged execution tools.
- If `predicted_category == "likely_scam"`, flag message in UI with warning badge and require manual HITL approval before taking any action.
