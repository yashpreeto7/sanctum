"""
Safe Workspace File Explorer Tool for Personal AI OS.
Allows reading, listing, and writing files within the project workspace.
"""
import os
from pathlib import Path
from typing import Dict, Any, List

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]

def list_workspace_files(subpath: str = "") -> List[Dict[str, Any]]:
    """List directory contents within the workspace."""
    target_dir = (WORKSPACE_ROOT / subpath).resolve()
    if not str(target_dir).startswith(str(WORKSPACE_ROOT)):
        return [{"error": "Access denied: Path outside workspace."}]
    
    if not target_dir.exists():
        return [{"error": f"Path not found: {subpath}"}]
    
    items = []
    for entry in target_dir.iterdir():
        if entry.name.startswith(".") or entry.name == "__pycache__":
            continue
        items.append({
            "name": entry.name,
            "is_dir": entry.is_dir(),
            "size": entry.stat().st_size if entry.is_file() else None,
            "path": str(entry.relative_to(WORKSPACE_ROOT)).replace("\\", "/")
        })
    return items

def read_workspace_file(file_path: str, max_chars: int = 4000) -> Dict[str, Any]:
    """Read contents of a workspace file."""
    target_file = (WORKSPACE_ROOT / file_path).resolve()
    if not str(target_file).startswith(str(WORKSPACE_ROOT)):
        return {"error": "Access denied: Path outside workspace."}
    
    if not target_file.exists() or not target_file.is_file():
        return {"error": f"File not found: {file_path}"}
    
    try:
        content = target_file.read_text(encoding="utf-8", errors="replace")
        truncated = len(content) > max_chars
        return {
            "path": file_path,
            "content": content[:max_chars],
            "truncated": truncated,
            "total_chars": len(content)
        }
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

def write_workspace_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write text contents to a workspace file."""
    target_file = (WORKSPACE_ROOT / file_path).resolve()
    if not str(target_file).startswith(str(WORKSPACE_ROOT)):
        return {"error": "Access denied: Path outside workspace."}
    
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "path": str(target_file.relative_to(WORKSPACE_ROOT)).replace("\\", "/"),
            "bytes_written": len(content.encode("utf-8"))
        }
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}
