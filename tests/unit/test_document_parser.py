"""
Unit tests for DocumentParser in Personal AI OS.
"""
from pathlib import Path
import pytest
from execution.tools.document_parser import DocumentParser


@pytest.fixture
def parser():
    return DocumentParser()


def test_parse_csv(tmp_path: Path, parser: DocumentParser):
    csv_file = tmp_path / "server_metrics.csv"
    csv_file.write_text(
        "timestamp,cpu_usage,memory_mb,request_count\n"
        "2026-08-29T10:00:00,12.5,1024,450\n"
        "2026-08-29T10:01:00,18.2,1080,520\n"
        "2026-08-29T10:02:00,14.0,1050,480\n",
        encoding="utf-8"
    )

    parsed = parser.parse_document(csv_file)
    assert parsed["doc_type"] == "dataset"
    assert "Server Metrics" in parsed["title"]
    assert len(parsed["metadata"]["columns"]) == 4
    assert parsed["metadata"]["numeric_statistics"]["cpu_usage"]["min"] == 12.5
    assert parsed["metadata"]["numeric_statistics"]["cpu_usage"]["max"] == 18.2

    note_md = parser.format_as_obsidian_note(parsed)
    assert "# Server Metrics" in note_md
    assert "| `cpu_usage` |" in note_md


def test_parse_text_and_classification(tmp_path: Path, parser: DocumentParser):
    doc_file = tmp_path / "vllm_architecture_spec.md"
    doc_file.write_text(
        "# vLLM Architecture & PagedAttention Spec\n\n"
        "This specification outlines the memory optimization and KV cache block paging design.\n\n"
        "## Key Highlights\n"
        "- Non-contiguous physical memory allocation\n"
        "- Zero memory fragmentation\n",
        encoding="utf-8"
    )

    parsed = parser.parse_document(doc_file)
    assert parsed["doc_type"] == "technical_spec"
    assert "vLLM Architecture" in parsed["title"]
    assert len(parsed["key_takeaways"]) >= 1

    note_md = parser.format_as_obsidian_note(parsed)
    assert "vLLM Architecture" in note_md
    assert "Non-contiguous physical memory allocation" in note_md


def test_classify_invoice(tmp_path: Path, parser: DocumentParser):
    invoice_file = tmp_path / "cloud_invoice_august.txt"
    invoice_file.write_text(
        "AWS Cloud Services Billing\n"
        "Invoice #: INV-2026-8839\n"
        "Invoice Date: 2026-08-28\n"
        "Subtotal: $450.00\n"
        "Tax: $45.00\n"
        "Total Amount: $495.00\n",
        encoding="utf-8"
    )

    parsed = parser.parse_document(invoice_file)
    assert parsed["doc_type"] == "invoice_financial"
    assert "#finance" in parsed["tags"]
