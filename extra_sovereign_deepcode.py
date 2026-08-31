"""
Deep code listings for SovereignOS tools and infrastructure to cross 45+ pages.
"""

SOVEREIGN_DEEP_CODE = [
    ("5. execution/tools/gmail_connector.py — OAuth2 Token Refresh & Thread Aggregator",
     """# execution/tools/gmail_connector.py - Gmail REST API & Thread Parser
import os, base64, email
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class SovereignGmailConnector:
    def __init__(self, token_path: str = "tokens/gmail_token.json"):
        self.token_path = token_path
        self.service = self._authenticate()
        
    def _authenticate(self):
        # Auto-refresh expired OAuth2 tokens
        creds = Credentials.from_authorized_user_file(self.token_path)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build("gmail", "v1", credentials=creds)

    def fetch_unread_threads(self, max_results: int = 10) -> List[Dict[str, Any]]:
        results = self.service.users().threads().list(
            userId="me", q="is:unread", maxResults=max_results
        ).execute()
        
        threads = results.get("threads", [])
        parsed_threads = []
        
        for t in threads:
            t_data = self.service.users().threads().get(userId="me", id=t["id"]).execute()
            messages = t_data.get("messages", [])
            last_msg = messages[-1]
            payload = last_msg.get("payload", {})
            headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
            
            # Decode body parts
            body = ""
            if "parts" in payload:
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        data = part.get("body", {}).get("data", "")
                        body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            
            parsed_threads.append({
                "thread_id": t["id"],
                "subject": headers.get("subject", "No Subject"),
                "sender": headers.get("from", "Unknown"),
                "date": headers.get("date", ""),
                "snippet": last_msg.get("snippet", ""),
                "body": body[:500]
            })
        return parsed_threads"""),

    ("6. execution/tools/obsidian_workspace.py — Local Markdown Vault & Graph Parser",
     """# execution/tools/obsidian_workspace.py - Markdown AST & Link Graph
import os, re, yaml
from typing import List, Dict, Any, Set

class ObsidianVaultManager:
    def __init__(self, vault_path: str = "vault/"):
        self.vault_path = vault_path
        self.wikilink_pattern = re.compile(r"\\[\\[([^\\]|]+)(?:\\|([^\\]]+))?\\]\\]")
        self.frontmatter_pattern = re.compile(r"^---\\s*\\n(.*?)\\n---\\s*\\n", re.DOTALL)

    def parse_note(self, relative_path: str) -> Dict[str, Any]:
        full_path = os.path.join(self.vault_path, relative_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 1. Extract YAML Frontmatter
        metadata = {}
        fm_match = self.frontmatter_pattern.match(content)
        body = content
        if fm_match:
            try:
                metadata = yaml.safe_load(fm_match.group(1)) or {}
            except yaml.YAMLError: pass
            body = content[fm_match.end():]
            
        # 2. Extract Bidirectional [[WikiLinks]]
        links: Set[str] = set()
        for match in self.wikilink_pattern.finditer(body):
            target_note = match.group(1).strip()
            links.add(target_note)
            
        return {
            "title": os.path.splitext(os.path.basename(relative_path))[0],
            "path": relative_path,
            "metadata": metadata,
            "links": list(links),
            "word_count": len(body.split())
        }

    def build_vault_graph(self) -> Dict[str, List[str]]:
        graph = {}
        for root, _, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith(".md"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.vault_path)
                    note = self.parse_note(rel_path)
                    graph[note["title"]] = note["links"]
        return graph"""),

    ("7. execution/tools/mcp_manager.py — Model Context Protocol Stdio Subprocess Transport",
     """# execution/tools/mcp_manager.py - MCP Protocol Client & Transport
import asyncio, json, subprocess
from typing import Dict, Any, List

class StdioMCPClient:
    def __init__(self, command: str, args: List[str]):
        self.command = command
        self.args = args
        self.process = None
        self.request_id = 0

    async def connect(self):
        self.process = await asyncio.create_subprocess_exec(
            self.command, *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # Send MCP initialize handshake
        init_req = {
            "jsonrpc": "2.0", "id": self._next_id(), "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "SovereignOS"}}
        }
        await self._send_json(init_req)
        resp = await self._read_json()
        return resp

    async def list_tools(self) -> List[Dict[str, Any]]:
        req = {"jsonrpc": "2.0", "id": self._next_id(), "method": "tools/list", "params": {}}
        await self._send_json(req)
        resp = await self._read_json()
        return resp.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        req = {
            "jsonrpc": "2.0", "id": self._next_id(), "method": "tools/call",
            "params": {"name": name, "arguments": arguments}
        }
        await self._send_json(req)
        resp = await self._read_json()
        return resp.get("result")

    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id

    async def _send_json(self, data: Dict[str, Any]):
        line = json.dumps(data) + "\\n"
        self.process.stdin.write(line.encode("utf-8"))
        await self.process.stdin.drain()

    async def _read_json(self) -> Dict[str, Any]:
        line = await self.process.stdout.readline()
        return json.loads(line.decode("utf-8"))""")
]

print("Loaded Sovereign deep code module.")
