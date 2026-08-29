# Meeting Preparation Automation

## Goal
Automatically assemble comprehensive preparation dossiers for upcoming meetings by extracting attendee history, prior email threads, relevant project notes, and open action items.

## Inputs
- Meeting title, start time, and attendee list (from Google Calendar).
- Search query targeting attendee email addresses and company names.
- Obsidian knowledge vault search for related topic notes.

## Execution Steps
1. **Identify Target Meeting**: Query `calendar_connector.list_events()` for upcoming events in the next 24-48 hours.
2. **Collect Attendee Context**:
   - Extract email addresses from attendee list.
   - Search recent correspondence via `gmail_connector.search_emails(f"from:{attendee_email}")`.
   - Identify last exchanged messages, agreed action items, and pending requests.
3. **Retrieve Project Documents**:
   - Query `obsidian_connector.search_notes(query=meeting_topic)` and `HybridRetriever`.
4. **Compile Prep Dossier**:
   - **Meeting Details**: Title, Time, Link, Attendees.
   - **Background & Relationship History**: Who they are and key topics discussed previously.
   - **Key Objectives & Talking Points**: Suggested questions, proposals, and decisions needed.
   - **Open Commitments**: Items promised to them or requested by them in prior threads.
5. **Output**: Display in Personal AI OS chat and optionally write to `Obsidian/Meetings/YYYY-MM-DD - Meeting Name.md`.

## Scripts Used
- `execution/tools/calendar_connector.py` — Retrieves meeting details & attendees.
- `execution/tools/gmail_connector.py` — Fetches past communications with attendees.
- `execution/tools/obsidian_connector.py` — Searches and writes meeting notes.
- `execution/orchestration/graph.py` — Orchestrates synthesis and structured dossier.

## Outputs
- Structured meeting dossier in UI.
- Saved note in Obsidian with tags `#meeting #prep`.
