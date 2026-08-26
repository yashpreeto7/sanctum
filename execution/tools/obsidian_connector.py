"""Deterministic Obsidian Vault Markdown Tool.

Manages private markdown notes, architecture decisions, and daily logs directly on disk.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from execution.core.config import settings


class ObsidianNote(BaseModel):
    """Represents a markdown note in the Obsidian vault."""

    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    folder: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ObsidianConnector:
    """Manages reading, writing, and searching notes inside an Obsidian vault."""

    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or settings.OBSIDIAN_VAULT_PATH or (settings.TEMP_DIR / "obsidian_vault")
        self.vault_path.mkdir(parents=True, exist_ok=True)

    def create_or_update_note(self, note: ObsidianNote) -> Dict[str, Any]:
        """Creates or updates a markdown note file."""
        target_dir = self.vault_path / (note.folder or "")
        target_dir.mkdir(parents=True, exist_ok=True)

        clean_filename = f"{note.title.replace('/', '_').replace('\\', '_')}.md"
        file_path = target_dir / clean_filename

        frontmatter_tags = f"tags: [{', '.join(note.tags)}]\n" if note.tags else ""
        formatted_content = (
            f"---\n"
            f"title: {note.title}\n"
            f"created: {note.created_at}\n"
            f"{frontmatter_tags}"
            f"---\n\n"
            f"{note.content}\n"
        )

        file_path.write_text(formatted_content, encoding="utf-8")

        return {
            "status": "success",
            "file_path": str(file_path),
            "title": note.title,
            "bytes_written": len(formatted_content),
        }

    def append_daily_log(self, entry: str, section: str = "AI Actions") -> Dict[str, Any]:
        """Appends an entry to today's daily note."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_folder = self.vault_path / "Daily"
        daily_folder.mkdir(parents=True, exist_ok=True)

        daily_file = daily_folder / f"{today_str}.md"
        timestamp = datetime.now().strftime("%H:%M:%S")

        entry_line = f"- **[{timestamp}]** {entry}\n"

        if daily_file.exists():
            content = daily_file.read_text(encoding="utf-8")
            if f"## {section}" in content:
                content = content.replace(f"## {section}\n", f"## {section}\n{entry_line}")
            else:
                content += f"\n## {section}\n{entry_line}"
        else:
            content = f"# Daily Note — {today_str}\n\n## {section}\n{entry_line}"

        daily_file.write_text(content, encoding="utf-8")
        return {"status": "success", "daily_file": str(daily_file), "timestamp": timestamp}

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Searches markdown note titles and contents within the vault."""
        matches = []
        q = query.lower()
        for md_file in self.vault_path.rglob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8")
                if q in md_file.name.lower() or q in text.lower():
                    matches.append({
                        "file_path": str(md_file),
                        "title": md_file.stem,
                        "preview": text[:200],
                    })
            except Exception:
                continue
        return matches


# Singleton instance
obsidian_connector = ObsidianConnector()
