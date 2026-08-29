# Daily Morning Briefing Routine

## Goal
Generate a concise, executive-level morning briefing for Yashpreet summarizing:
1. Today's scheduled calendar events and potential meeting conflicts.
2. Unread high-priority emails categorized as Important or Job/Career.
3. Relevant task items and active sprint priorities from Obsidian notes.

## Inputs
- Current date and local time.
- Google Calendar events for the current day (start of day to end of day).
- Unread emails from Gmail categorized via the ML Triaging Gatekeeper.
- User context retrieved via Hybrid RAG from Obsidian knowledge vault.

## Execution Steps
1. **Fetch Calendar Events**: Call `calendar_connector.list_events()` for the current day's time window.
2. **Fetch Inbound High-Priority Emails**: Call `gmail_connector.list_unread(max_results=10)` and filter through `TriagingClassifier`.
3. **Retrieve Task Context**: Query `HybridRetriever` with `"daily tasks active priorities goals"` to get relevant Obsidian vault snippets.
4. **Synthesize Executive Summary**:
   - Section 1: 📅 **Today's Agenda & Schedule** (chronological list of meetings + Google Meet/Zoom links).
   - Section 2: ⚡ **Action Items & Urgent Emails** (senders, topics, required follow-ups).
   - Section 3: 🎯 **Focus Areas for Today** (synthesized from tasks and upcoming deadlines).
5. **Delivery**: Present via interactive chat dashboard or stream through JARVIS voice engine on request.

## Scripts Used
- `execution/tools/calendar_connector.py` — Fetches today's events from Google Calendar.
- `execution/tools/gmail_connector.py` — Fetches unread inbound emails.
- `execution/ml/triaging_classifier.py` — Filters out marketing, spam, and noise.
- `execution/rag/hybrid_retriever.py` — Pulls user context and vault notes.
- `execution/orchestration/graph.py` — Synthesizes structured markdown response.

## Outputs
- Formatted markdown morning report displayed on dashboard or read aloud via audio synthesis.
- Optional synced note in Obsidian: `Daily Notes/YYYY-MM-DD.md`.

## Edge Cases & Learnings
- **No events on calendar**: Clearly state "Your calendar is completely open today — great time for deep work."
- **Overlapping meetings**: Highlight overlapping time blocks in bold with an alert badge.
- **Timezone alignment**: Ensure ISO timestamps are converted to local user timezone (IST / local system clock).
