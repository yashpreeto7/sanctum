"""MCP Server Hub and Multi-Server Orchestration Manager for SovereignOS."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from execution.tools.mcp_client import MCPClient

logger = logging.getLogger("SovereignOS.MCPManager")
logger.setLevel(logging.INFO)

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "mcp_servers.json"


DEFAULT_TEMPLATES = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "c:/Users/Yashpreet_o7/Desktop/PERSONALAGENT"],
        "env": {},
        "enabled": False,
        "description": "Local file system operations, reading directories, writing and searching files.",
    },
    "sqlite": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "c:/Users/Yashpreet_o7/Desktop/PERSONALAGENT/data/sovereign.db"],
        "env": {},
        "enabled": False,
        "description": "Direct SQLite querying, table introspection, and analytical queries.",
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
        "enabled": False,
        "description": "Interact with GitHub repositories, pull requests, issues, and code search.",
    },
    "brave_search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {"BRAVE_API_KEY": ""},
        "enabled": False,
        "description": "High-privacy global web and news search via Brave Search API.",
    },
}


class MCPManager:
    """Central registry and lifecycle manager for all configured MCP servers."""

    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.clients: Dict[str, MCPClient] = {}
        self.server_configs: Dict[str, Dict[str, Any]] = {}
        self._load_configs()

    def _load_configs(self):
        """Loads configured servers from disk or initializes defaults."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.server_configs = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load MCP servers config: {e}")
                self.server_configs = DEFAULT_TEMPLATES.copy()
        else:
            self.server_configs = DEFAULT_TEMPLATES.copy()
            self._save_configs()

    def _save_configs(self):
        """Persists server configurations to disk."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.server_configs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save MCP servers config: {e}")

    async def start_all_enabled(self):
        """Starts all MCP servers marked as enabled in configuration."""
        tasks = []
        for name, cfg in self.server_configs.items():
            if cfg.get("enabled", False):
                tasks.append(self.start_server(name))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def start_server(self, name: str) -> bool:
        """Instantiates and starts an MCP server by name."""
        if name not in self.server_configs:
            logger.warning(f"Cannot start unknown MCP server: '{name}'")
            return False

        if name in self.clients and self.clients[name].is_running:
            return True

        cfg = self.server_configs[name]
        client = MCPClient(
            name=name,
            command=cfg.get("command", ""),
            args=cfg.get("args", []),
            env=cfg.get("env", {}),
            cwd=cfg.get("cwd", None),
            timeout=cfg.get("timeout", 30.0),
        )
        success = await client.start()
        if success:
            self.clients[name] = client
            return True
        else:
            logger.error(f"Failed to start MCP server '{name}'")
            return False

    async def stop_server(self, name: str):
        """Stops an active MCP server."""
        if name in self.clients:
            await self.clients[name].close()
            del self.clients[name]

    async def stop_all(self):
        """Stops all running MCP servers."""
        for name in list(self.clients.keys()):
            await self.stop_server(name)

    async def add_or_update_server(self, name: str, config: Dict[str, Any], auto_start: bool = True) -> bool:
        """Adds or updates a server configuration and restarts if enabled."""
        was_running = name in self.clients and self.clients[name].is_running
        if was_running:
            await self.stop_server(name)

        self.server_configs[name] = config
        self._save_configs()

        if config.get("enabled", False) and auto_start:
            return await self.start_server(name)
        return True

    async def delete_server(self, name: str) -> bool:
        """Deletes a server configuration and stops it if running."""
        if name in self.server_configs:
            await self.stop_server(name)
            del self.server_configs[name]
            self._save_configs()
            return True
        return False

    def list_servers_status(self) -> List[Dict[str, Any]]:
        """Returns status summary for all configured servers."""
        results = []
        for name, cfg in self.server_configs.items():
            client = self.clients.get(name)
            is_running = client.is_running if client else False
            tool_count = len(client.discovered_tools) if client and is_running else 0
            results.append({
                "name": name,
                "command": cfg.get("command", ""),
                "args": cfg.get("args", []),
                "env": cfg.get("env", {}),
                "enabled": cfg.get("enabled", False),
                "description": cfg.get("description", ""),
                "is_running": is_running,
                "tool_count": tool_count,
                "server_info": client.server_info if client and is_running else {},
            })
        return results

    def list_all_tools(self) -> List[Dict[str, Any]]:
        """Aggregates all discovered tools across all active MCP servers with namespacing."""
        all_tools = []
        for name, client in self.clients.items():
            if client.is_running:
                for tool in client.discovered_tools:
                    tool_copy = tool.copy()
                    tool_copy["server_name"] = name
                    tool_copy["namespaced_name"] = f"mcp:{name}:{tool.get('name')}"
                    all_tools.append(tool_copy)
        return all_tools

    async def call_namespaced_tool(self, namespaced_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dispatches a tool call using namespaced format 'mcp:{server}:{tool}'."""
        parts = namespaced_name.split(":", 2)
        if len(parts) != 3 or parts[0] != "mcp":
            raise ValueError(f"Invalid namespaced MCP tool identifier: '{namespaced_name}'. Expected 'mcp:<server>:<tool>'")

        server_name = parts[1]
        tool_name = parts[2]

        client = self.clients.get(server_name)
        if not client or not client.is_running:
            raise RuntimeError(f"MCP Server '{server_name}' is not running or active.")

        return await client.call_tool(tool_name, arguments or {})


# Singleton instance
mcp_manager = MCPManager()
