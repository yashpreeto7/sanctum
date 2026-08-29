"""
Unit tests for FolderWatcher and automated ingestion in Personal AI OS.
"""
from pathlib import Path
import pytest
from execution.tools.folder_watcher import FolderWatcher


@pytest.fixture
def folder_watcher(tmp_path: Path):
    drop_dir = tmp_path / "inbox_drop"
    vault_dir = tmp_path / "vault"
    drop_dir.mkdir()
    vault_dir.mkdir()
    return FolderWatcher(drop_dir=drop_dir, vault_dir=vault_dir)


def test_folder_watcher_scan_and_ingest(folder_watcher: FolderWatcher):
    # Drop a sample markdown specification
    sample_file = folder_watcher.drop_dir / "qdrant_indexing_spec.md"
    sample_file.write_text(
        "# Qdrant Dense Vector Indexing Architecture\n\n"
        "Details on cosine distance, HNSW parameters, and payload filtering for Personal AI OS.\n\n"
        "## Takeaways\n"
        "- Sub-millisecond similarity queries\n"
        "- Payload filtered search by timestamp\n",
        encoding="utf-8"
    )

    # 1. Scan and ingest
    processed = folder_watcher.scan_and_ingest_all()
    assert len(processed) == 1
    assert processed[0]["filename"] == "qdrant_indexing_spec.md"
    assert processed[0]["doc_type"] == "technical_spec"

    # 2. Verify second scan skips already processed file
    processed_again = folder_watcher.scan_and_ingest_all()
    assert len(processed_again) == 0

    # 3. Verify Obsidian note was saved
    doc_notes = list((folder_watcher.vault_dir / "Documents").rglob("*.md"))
    assert len(doc_notes) == 1
    assert "Qdrant Dense Vector Indexing Architecture" in doc_notes[0].read_text(encoding="utf-8")

    # 4. Check manifest listing
    doc_list = folder_watcher.list_processed_documents()
    assert len(doc_list) == 1
    assert doc_list[0]["filename"] == "qdrant_indexing_spec.md"
