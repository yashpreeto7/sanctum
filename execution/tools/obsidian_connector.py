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

    def list_all_notes(self) -> List[Dict[str, Any]]:
        """Lists all markdown files in the vault with metadata and frontmatter tags."""
        notes = []
        for md_file in sorted(self.vault_path.rglob("*.md"), key=lambda f: f.stat().st_mtime if f.exists() else 0, reverse=True):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                rel_path = md_file.relative_to(self.vault_path).as_posix()
                folder = md_file.parent.relative_to(self.vault_path).as_posix()
                if folder == ".":
                    folder = "Root"

                # Extract frontmatter tags & title if present
                tags = []
                title = md_file.stem
                body_preview = content
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        fm = parts[1]
                        body_preview = parts[2].strip()
                        for line in fm.splitlines():
                            if line.startswith("title:"):
                                title = line.split("title:", 1)[1].strip()
                            elif line.startswith("tags:"):
                                tags_str = line.split("tags:", 1)[1].strip().strip("[]")
                                tags = [t.strip().strip("'\"") for t in tags_str.split(",") if t.strip()]

                stat = md_file.stat()
                notes.append({
                    "title": title,
                    "filename": md_file.name,
                    "rel_path": rel_path,
                    "folder": folder,
                    "tags": tags,
                    "preview": body_preview[:160].replace("\n", " ").strip(),
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_daily": folder.lower() == "daily" or md_file.parent.name.lower() == "daily",
                })
            except Exception:
                continue
        return notes

    def read_note(self, rel_path: str) -> Optional[Dict[str, Any]]:
        """Reads a specific note by relative path."""
        target = self.vault_path / rel_path
        if not target.exists() or not target.is_file():
            # Try searching by stem/filename
            for f in self.vault_path.rglob("*.md"):
                if f.name == rel_path or f.stem == rel_path:
                    target = f
                    break
        if not target.exists():
            return None

        content = target.read_text(encoding="utf-8", errors="ignore")
        stat = target.stat()
        return {
            "title": target.stem,
            "filename": target.name,
            "rel_path": target.relative_to(self.vault_path).as_posix(),
            "folder": target.parent.relative_to(self.vault_path).as_posix(),
            "content": content,
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    def delete_note(self, rel_path: str) -> bool:
        """Deletes a note file."""
        target = self.vault_path / rel_path
        if target.exists() and target.is_file():
            target.unlink()
            return True
        return False


# Singleton instance
obsidian_connector = ObsidianConnector()

