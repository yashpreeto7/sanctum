"""
Document Parser for Personal AI OS.
Extracts structured content, metadata, tabular schemas, and insights from PDFs, CSVs, and text files.
"""
from datetime import datetime
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import pandas as pd
from pypdf import PdfReader


class DocumentParser:
    """Multi-format parser for universal local document ingestion."""

    def __init__(self):
        pass

    def parse_document(self, file_path: str | Path) -> Dict[str, Any]:
        """
        Main entrypoint: parses file based on extension and returns structured document representation.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()
        file_stats = path.stat()

        base_info = {
            "filename": path.name,
            "filepath": str(path.resolve()),
            "filesize_bytes": file_stats.st_size,
            "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "extension": suffix,
        }

        if suffix == ".pdf":
            parsed = self.parse_pdf(path)
        elif suffix in [".csv", ".tsv"]:
            parsed = self.parse_csv(path)
        elif suffix in [".md", ".markdown", ".txt", ".json", ".py", ".log"]:
            parsed = self.parse_text(path)
        else:
            # Fallback text attempt
            try:
                parsed = self.parse_text(path)
            except Exception:
                parsed = {
                    "doc_type": "binary_unknown",
                    "title": path.stem.replace("_", " ").title(),
                    "text_content": f"Binary file: {path.name} ({file_stats.st_size} bytes)",
                    "summary": f"Unparsed binary file {path.name}",
                    "tags": ["#file", "#raw"],
                    "metadata": {},
                }

        return {**base_info, **parsed}

    def parse_pdf(self, path: Path) -> Dict[str, Any]:
        """Extract text, metadata, and section structure from PDF using pypdf."""
        reader = PdfReader(str(path))
        num_pages = len(reader.pages)
        pages_text: List[str] = []

        for idx, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
                pages_text.append(text.strip())
            except Exception:
                pages_text.append("")

        full_text = "\n\n".join(pages_text)
        meta = reader.metadata or {}
        pdf_title = getattr(meta, "title", None) or path.stem.replace("_", " ").replace("-", " ").title()
        pdf_author = getattr(meta, "author", None) or "Unknown Author"

        doc_type = self._classify_text_type(full_text, path.name)
        extracted = self._extract_specific_pdf_insights(full_text, doc_type, pdf_title, pdf_author)

        return {
            "doc_type": doc_type,
            "title": extracted.get("title", pdf_title),
            "pages_count": num_pages,
            "text_content": full_text,
            "summary": extracted.get("summary", ""),
            "key_takeaways": extracted.get("key_takeaways", []),
            "tags": extracted.get("tags", ["#document", "#pdf"]),
            "metadata": {
                "author": pdf_author,
                "pages": num_pages,
                "pdf_metadata": {k: str(v) for k, v in meta.items()} if meta else {},
                **extracted.get("custom_meta", {}),
            },
        }

    def parse_csv(self, path: Path) -> Dict[str, Any]:
        """Extract tabular schemas, statistical distributions, and records from CSV/TSV."""
        sep = "\t" if path.suffix.lower() == ".tsv" else ","
        try:
            df = pd.read_csv(path, sep=sep, nrows=1000)
        except Exception:
            df = pd.read_csv(path, sep=sep, on_bad_lines="skip", nrows=1000)

        total_rows = len(df)
        columns = list(df.columns)
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        stats_summary: Dict[str, Any] = {}
        for col in numeric_cols[:6]:
            stats_summary[col] = {
                "mean": round(float(df[col].mean()), 2) if not pd.isna(df[col].mean()) else None,
                "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
            }

        # Sample preview (top 5 rows)
        preview_records = df.head(5).to_dict(orient="records")

        # Convert to text representation for embeddings
        try:
            preview_text = df.head(15).to_markdown(index=False)
        except Exception:
            header_row = "| " + " | ".join(str(c) for c in columns) + " |"
            sep_row = "| " + " | ".join("---" for _ in columns) + " |"
            data_rows = []
            for _, row in df.head(10).iterrows():
                data_rows.append("| " + " | ".join(str(v) for v in row.values) + " |")
            preview_text = "\n".join([header_row, sep_row] + data_rows)

        text_repr = f"CSV Dataset: {path.name}\nColumns: {', '.join(columns)}\nRows Sampled: {total_rows}\n\nData Preview:\n{preview_text}"

        title = path.stem.replace("_", " ").replace("-", " ").title()
        summary = f"Tabular dataset with {len(columns)} columns ({', '.join(columns[:5])}...) and {total_rows}+ rows."

        return {
            "doc_type": "dataset",
            "title": title,
            "text_content": text_repr,
            "summary": summary,
            "key_takeaways": [
                f"Contains {len(columns)} dimensions: {', '.join(columns[:8])}",
                f"Numeric columns analyzed: {', '.join(numeric_cols[:4])}" if numeric_cols else "Categorical dataset",
                f"Sample size: {total_rows} rows parsed",
            ],
            "tags": ["#dataset", "#csv", "#data-table"],
            "metadata": {
                "columns": columns,
                "total_rows_sampled": total_rows,
                "numeric_statistics": stats_summary,
                "preview_records": preview_records,
            },
        }

    def parse_text(self, path: Path) -> Dict[str, Any]:
        """Extract text, headers, and code snippets from Markdown/Text files."""
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        title = path.stem.replace("_", " ").replace("-", " ").title()
        # Check first markdown heading
        heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()

        doc_type = self._classify_text_type(content, path.name)
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        summary = paragraphs[0][:300] if paragraphs else "Empty document"
        if len(paragraphs) > 0 and paragraphs[0].startswith("#"):
            summary = paragraphs[1][:300] if len(paragraphs) > 1 else paragraphs[0]

        # Extract bullet takeaways
        bullets = re.findall(r"^[-*]\s+(.+)$", content, re.MULTILINE)

        return {
            "doc_type": doc_type,
            "title": title,
            "text_content": content,
            "summary": summary,
            "key_takeaways": bullets[:5] if bullets else [summary[:120]],
            "tags": self._get_tags_for_type(doc_type),
            "metadata": {
                "line_count": len(content.splitlines()),
                "char_count": len(content),
            },
        }

    def _classify_text_type(self, text: str, filename: str) -> str:
        """Classify document category based on heuristics and keyword density."""
        lower = text.lower()
        lower_fn = filename.lower()

        if any(w in lower_fn or w in lower for w in ["invoice", "receipt", "billing", "amount due", "payment", "subtotal", "tax id", "usd $", "inr ₹"]):
            if "total" in lower or "invoice #" in lower or "receipt" in lower_fn:
                return "invoice_financial"

        if any(w in lower_fn or w in lower for w in ["abstract", "arxiv", "methodology", "references", "doi:", "et al.", "proceedings", "neural", "benchmark"]):
            return "research_paper"

        if any(w in lower_fn or w in lower for w in ["architecture", "rfc", "design doc", "specification", "api doc", "endpoint", "system design"]):
            return "technical_spec"

        if any(w in lower_fn or w in lower for w in ["meeting", "agenda", "minutes", "action items", "attendees", "sync call"]):
            return "meeting_notes"

        return "general_doc"

    def _extract_specific_pdf_insights(self, text: str, doc_type: str, fallback_title: str, author: str) -> Dict[str, Any]:
        """Extract structured insights tailored for specific document categories."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        top_text = "\n".join(lines[:25])

        if doc_type == "research_paper":
            abstract_match = re.search(r"(?i)abstract[:\s]*(.*?)(?=(introduction|1\.|background|\n\n[A-Z]))", text, re.DOTALL)
            abstract = abstract_match.group(1).strip()[:600] if abstract_match else (lines[1] if len(lines) > 1 else "")
            
            # Find title from top lines
            title = lines[0] if lines and len(lines[0]) < 120 else fallback_title
            
            # Extract key conclusions or methodology mentions
            takeaways = []
            if abstract:
                takeaways.append(f"Abstract Summary: {abstract[:200]}...")
            
            methods = re.findall(r"(?i)(?:we propose|our approach|we introduce|results show|demonstrates that)\s+([^.\n]+)", text)
            for m in methods[:3]:
                takeaways.append(m.strip().capitalize())

            return {
                "title": title,
                "summary": abstract or f"Research publication by {author}",
                "key_takeaways": takeaways if takeaways else ["Academic research publication parsed."],
                "tags": ["#research", "#paper", "#arxiv", "#academic"],
                "custom_meta": {"abstract": abstract},
            }

        elif doc_type == "invoice_financial":
            # Extract total amount
            amount_match = re.search(r"(?i)(?:total|amount due|balance due|grand total)[\s:]*([$₹€£]?\s*[\d,]+\.\d{2})", text)
            total_amt = amount_match.group(1) if amount_match else "Unknown Amount"

            invoice_no_match = re.search(r"(?i)(?:invoice\s*#?|inv-?)\s*([A-Za-z0-9-_]+)", text)
            invoice_no = invoice_no_match.group(1) if invoice_no_match else "N/A"

            date_match = re.search(r"(?i)(?:date|invoice date)[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}|[A-Za-z]+\s+[0-9]{1,2},\s+[0-9]{4})", text)
            inv_date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

            return {
                "title": f"Invoice {invoice_no} ({total_amt})",
                "summary": f"Financial invoice/receipt. Total Amount: {total_amt}, Date: {inv_date}",
                "key_takeaways": [
                    f"Invoice Reference: {invoice_no}",
                    f"Total Billed: {total_amt}",
                    f"Date: {inv_date}",
                ],
                "tags": ["#finance", "#invoice", "#receipt", "#expenses"],
                "custom_meta": {
                    "total_amount": total_amt,
                    "invoice_number": invoice_no,
                    "invoice_date": inv_date,
                },
            }

        else:
            summary = lines[0] if lines else "Document imported"
            return {
                "title": fallback_title,
                "summary": summary[:300],
                "key_takeaways": [lines[i] for i in range(min(4, len(lines))) if len(lines[i]) > 10],
                "tags": self._get_tags_for_type(doc_type),
                "custom_meta": {},
            }

    def _get_tags_for_type(self, doc_type: str) -> List[str]:
        type_tag_map = {
            "research_paper": ["#research", "#paper", "#academic"],
            "invoice_financial": ["#finance", "#invoice", "#receipt"],
            "technical_spec": ["#spec", "#architecture", "#engineering"],
            "dataset": ["#data", "#dataset", "#csv"],
            "meeting_notes": ["#meeting", "#notes", "#agenda"],
            "general_doc": ["#document", "#vault"],
        }
        return type_tag_map.get(doc_type, ["#document"])

    def format_as_obsidian_note(self, parsed: Dict[str, Any]) -> str:
        """Format the parsed document into a clean Obsidian Markdown note with YAML frontmatter."""
        tags_str = " ".join(parsed.get("tags", ["#document"]))
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        meta_yaml = [
            "---",
            f"title: \"{parsed.get('title', 'Document')}\"",
            f"doc_type: {parsed.get('doc_type', 'general_doc')}",
            f"source_file: \"{parsed.get('filename', '')}\"",
            f"imported_at: {now_str}",
            f"tags: [{', '.join([t.replace('#', '') for t in parsed.get('tags', [])])}]",
            "---",
            "",
            f"# {parsed.get('title', 'Document')}",
            "",
            f"**File:** `{parsed.get('filename', '')}` | **Type:** `{parsed.get('doc_type', '')}` | **Tags:** {tags_str}",
            "",
            "## 📌 Executive Summary",
            f"{parsed.get('summary', 'No summary available.')}",
            "",
        ]

        if parsed.get("key_takeaways"):
            meta_yaml.append("## 🔑 Key Takeaways & Highlights")
            for item in parsed["key_takeaways"]:
                meta_yaml.append(f"- {item}")
            meta_yaml.append("")

        if parsed.get("doc_type") == "dataset" and "numeric_statistics" in parsed.get("metadata", {}):
            meta_yaml.append("## 📊 Dataset Statistics")
            stats = parsed["metadata"]["numeric_statistics"]
            if stats:
                meta_yaml.append("| Metric | Mean | Min | Max |")
                meta_yaml.append("| :--- | :--- | :--- | :--- |")
                for col, s in stats.items():
                    meta_yaml.append(f"| `{col}` | {s.get('mean')} | {s.get('min')} | {s.get('max')} |")
                meta_yaml.append("")

        meta_yaml.append("## 📄 Raw Extracted Content Preview")
        preview = parsed.get("text_content", "")[:1500]
        meta_yaml.append(f"```text\n{preview}\n...\n```")
        meta_yaml.append("")
        meta_yaml.append("---")
        meta_yaml.append(f"*Auto-indexed by Personal AI OS Universal Ingestion Pipeline on {now_str}*")

        return "\n".join(meta_yaml)
