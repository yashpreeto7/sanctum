# Smart Knowledge Vault Synchronization

## Goal
Extract durable facts, architectural decisions, technical nuggets, and key action items from incoming communications and save them cleanly into the user's Obsidian Knowledge Vault.

## Inputs
- Inbound email body, thread summary, or chat interaction text.
- Target topic/category (e.g., `Architecture`, `Career`, `Projects`, `Reference`).

## Execution Steps
1. **Fact Extraction**: Run through `DualLLMQuarantine` to isolate pure factual data (dates, links, instructions, code snippets).
2. **Determine Note Destination & Title**:
   - Check if an existing note covers this topic (`obsidian_connector.search_notes`).
   - If exists, append a new timestamped section.
   - If new, create a markdown note with clean YAML frontmatter and appropriate tags.
3. **Format Markdown**:
   - Title: `# [Subject / Topic]`
   - Metadata: `tags`, `source: email`, `created: YYYY-MM-DD`
   - Content: Bulleted insights, actionable items, code snippets, or reference links.
4. **Save Note**: Execute `obsidian_connector.create_note(...)`.

## Scripts Used
- `execution/security/quarantine_parser.py` — Sanitizes inputs before saving to markdown.
- `execution/tools/obsidian_connector.py` — Creates/searches markdown notes in the local vault.
- `execution/orchestration/graph.py` — LangGraph reasoning node for tool execution.

## Outputs
- Markdown file in local Obsidian vault with proper tags and bidirectional links.
