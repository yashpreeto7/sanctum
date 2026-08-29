"""
Folder Watcher and Document Ingestion Pipeline for Personal AI OS.
Monitors a drop folder (e.g., data/inbox_drop/) for incoming PDFs, CSVs, and notes,
extracts insights via DocumentParser, writes notes to Obsidian, and indexes vectors in Qdrant.
"""
import asyncio
from datetime import datetime
import json
import logging
from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional

from execution.tools.document_parser import DocumentParser
from execution.tools.obsidian_connector import ObsidianConnector

logger = logging.getLogger(__name__)


class FolderWatcher:
    """Watches a drop folder for incoming documents and automates their ingestion."""

    def __init__(
        self,
        drop_dir: Optional[Path] = None,
        vault_dir: Optional[Path] = None,
        vector_store=None,
    ):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.drop_dir = drop_dir or (base_dir / "data" / "inbox_drop")
        self.drop_dir.mkdir(parents=True, exist_ok=True)

        self.vault_dir = vault_dir or (base_dir / "data" / "knowledge_vault")
        self.state_file = self.drop_dir / ".processed_manifest.json"

        self.parser = DocumentParser()
        self.obsidian = ObsidianConnector(vault_path=self.vault_dir)
        self.vector_store = vector_store

        self._manifest = self._load_manifest()
        self._is_running = False
        self._thread: Optional[threading.Thread] = None

    def _load_manifest(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading manifest: {e}")
        return {"processed": {}, "last_scanned": None}

    def _save_manifest(self):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self._manifest, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving manifest: {e}")

    def list_processed_documents(self) -> List[Dict[str, Any]]:
        """Return list of all ingested document summaries sorted by ingestion time."""
        docs = list(self._manifest.get("processed", {}).values())
        docs.sort(key=lambda x: x.get("ingested_at", ""), reverse=True)
        return docs

    def process_file(self, file_path: Path | str, force: bool = False) -> Optional[Dict[str, Any]]:
        """Parse a single file, write to Obsidian, and index chunks into vector store."""
        path = Path(file_path)
        if not path.exists() or path.is_dir() or path.name.startswith("."):
            return None

        file_stat = path.stat()
        file_key = f"{path.name}_{file_stat.st_mtime}_{file_stat.st_size}"

        if not force and file_key in self._manifest.get("processed", {}):
            return self._manifest["processed"][file_key]

        logger.info(f"Processing dropped document: {path.name}")
        parsed = self.parser.parse_document(path)

        # 1. Save to Obsidian
        note_content = self.parser.format_as_obsidian_note(parsed)
        category_folder = "Documents"
        if parsed.get("doc_type") == "research_paper":
            category_folder = "Documents/Papers"
        elif parsed.get("doc_type") == "invoice_financial":
            category_folder = "Documents/Finance"
        elif parsed.get("doc_type") == "dataset":
            category_folder = "Documents/Datasets"

        safe_title = "".join(c for c in parsed.get("title", path.stem) if c.isalnum() or c in " -_").strip()
        note_path = f"{category_folder}/{safe_title}.md"
        
        try:
            self.obsidian.create_note(title=note_path, content=note_content)
        except Exception as e:
            logger.warning(f"Failed to write note to Obsidian: {e}")

        # 2. Ingest into Vector Store if available
        if self.vector_store is not None:
            try:
                self._index_into_vector_store(parsed)
            except Exception as e:
                logger.warning(f"Failed to index document in vector store: {e}")

        # 3. Update manifest
        record = {
            "file_key": file_key,
            "filename": path.name,
            "filepath": str(path.resolve()),
            "title": parsed.get("title", path.stem),
            "doc_type": parsed.get("doc_type", "general_doc"),
            "summary": parsed.get("summary", ""),
            "key_takeaways": parsed.get("key_takeaways", []),
            "tags": parsed.get("tags", []),
            "obsidian_path": note_path,
            "ingested_at": datetime.now().isoformat(),
            "filesize_bytes": file_stat.st_size,
        }

        self._manifest.setdefault("processed", {})[file_key] = record
        self._save_manifest()
        return record

    def _index_into_vector_store(self, parsed: Dict[str, Any]):
        """Chunk text and insert into Qdrant vector store with metadata."""
        text = parsed.get("text_content", "")
        if not text:
            return

        # Simple chunking by paragraph / character window
        chunk_size = 800
        overlap = 100
        chunks = []
        start = 0
        while start < len(text):
            chunk_text = text[start : start + chunk_size].strip()
            if chunk_text:
                chunks.append({
                    "id": f"{parsed.get('filename')}_{start}",
                    "text": chunk_text,
                    "metadata": {
                        "source": "document_drop",
                        "filename": parsed.get("filename"),
                        "doc_type": parsed.get("doc_type"),
                        "title": parsed.get("title"),
                        "timestamp": parsed.get("created_at", datetime.now().isoformat()),
                    },
                })
            start += chunk_size - overlap

        if hasattr(self.vector_store, "insert_chunks"):
            self.vector_store.insert_chunks(chunks)

    def scan_and_ingest_all(self) -> List[Dict[str, Any]]:
        """Scans drop directory for any new files and ingests them."""
        processed_now: List[Dict[str, Any]] = []
        if not self.drop_dir.exists():
            return processed_now

        for file_path in self.drop_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith("."):
                file_stat = file_path.stat()
                file_key = f"{file_path.name}_{file_stat.st_mtime}_{file_stat.st_size}"
                if file_key not in self._manifest.get("processed", {}):
                    result = self.process_file(file_path, force=True)
                    if result:
                        processed_now.append(result)

        self._manifest["last_scanned"] = datetime.now().isoformat()
        self._save_manifest()
        return processed_now

    def start_background_watcher(self, interval_seconds: int = 10):
        """Starts a lightweight daemon thread that periodically checks the drop directory."""
        if self._is_running:
            return

        self._is_running = True

        def _watch_loop():
            while self._is_running:
                try:
                    self.scan_and_ingest_all()
                except Exception as e:
                    logger.debug(f"Watcher scan error: {e}")
                time.sleep(interval_seconds)

        self._thread = threading.Thread(target=_watch_loop, daemon=True, name="FolderWatcherThread")
        self._thread.start()
        logger.info(f"FolderWatcher started on: {self.drop_dir}")

    def stop(self):
        """Stops the background watcher thread."""
        self._is_running = False
