"""Universal Model Context Protocol (MCP) Client for SovereignOS.

Implements JSON-RPC 2.0 stdio transport protocol for connecting to any standard
MCP server (GitHub, SQLite, Postgres, Slack, Notion, Brave Search, Filesystem, Puppeteer, etc.).
"""

import asyncio
import json
import logging
import os
import shutil
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger("SovereignOS.MCPClient")
logger.setLevel(logging.INFO)


class MCPClient:
    """Manages an active connection to an external MCP server via stdio transport."""

    def __init__(
        self,
        name: str,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.cwd = cwd
        self.timeout = timeout

        self.process: Optional[asyncio.subprocess.Process] = None
        self._request_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._reader_task: Optional[asyncio.Task] = None
        self._is_initialized = False
        self.server_info: Dict[str, Any] = {}
        self.capabilities: Dict[str, Any] = {}
        self.discovered_tools: List[Dict[str, Any]] = []

    @property
    def is_running(self) -> bool:
        return self.process is not None and self.process.returncode is None

    async def start(self) -> bool:
        """Spawns the MCP server subprocess and initiates handshake."""
        if self.is_running:
            return True

        # Resolve command path if needed (e.g. npx, python, node, uv)
        cmd_path = shutil.which(self.command) or self.command
        full_args = [cmd_path] + self.args

        # Build clean environment inheriting current process PATH
        process_env = os.environ.copy()
        for k, v in self.env.items():
            process_env[k] = str(v)

        logger.info(f"Starting MCP server '{self.name}': {' '.join(full_args)}")

        try:
            self.process = await asyncio.create_subprocess_exec(
                *full_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=process_env,
                cwd=self.cwd,
            )
        except Exception as e:
            logger.error(f"Failed to spawn MCP server '{self.name}': {e}")
            return False

        # Start background reader task for stdout
        self._reader_task = asyncio.create_task(self._listen_stdout())

        # Perform MCP initialize handshake
        try:
            init_res = await self._initialize()
            if init_res:
                self._is_initialized = True
                # Fetch available tools
                await self.list_tools()
                logger.info(f"MCP server '{self.name}' initialized successfully with {len(self.discovered_tools)} tools.")
                return True
            else:
                logger.warning(f"MCP server '{self.name}' initialization handshake failed.")
                await self.close()
                return False
        except Exception as e:
            logger.error(f"Error during MCP handshake for '{self.name}': {e}")
            await self.close()
            return False

    async def _listen_stdout(self):
        """Continuously reads line-delimited JSON-RPC messages from server stdout."""
        if not self.process or not self.process.stdout:
            return

        while self.is_running:
            try:
                line = await self.process.stdout.readline()
                if not line:
                    break

                line_str = line.decode("utf-8", errors="replace").strip()
                if not line_str:
                    continue

                try:
                    msg = json.loads(line_str)
                except json.JSONDecodeError:
                    # Ignore non-JSON logs (e.g. debug prints)
                    continue

                # Handle response
                if "id" in msg and msg["id"] in self._pending_requests:
                    future = self._pending_requests.pop(msg["id"])
                    if not future.done():
                        future.set_result(msg)
                elif "method" in msg:
                    # Server notifications or incoming requests (ping, notifications/message)
                    logger.debug(f"MCP server notification from '{self.name}': {msg.get('method')}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Reader exception on '{self.name}': {e}")
                break

    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sends a JSON-RPC 2.0 request and awaits response."""
        if not self.is_running or not self.process or not self.process.stdin:
            raise RuntimeError(f"MCP server '{self.name}' is not running.")

        self._request_id += 1
        req_id = self._request_id

        req = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_requests[req_id] = future

        msg_bytes = (json.dumps(req) + "\n").encode("utf-8")
        self.process.stdin.write(msg_bytes)
        await self.process.stdin.drain()

        try:
            res = await asyncio.wait_for(future, timeout=self.timeout)
            if "error" in res:
                err = res["error"]
                raise RuntimeError(f"MCP Error ({err.get('code', -1)}): {err.get('message', 'Unknown error')}")
            return res.get("result", {})
        except asyncio.TimeoutError:
            self._pending_requests.pop(req_id, None)
            raise TimeoutError(f"Request '{method}' to MCP server '{self.name}' timed out after {self.timeout}s.")

    async def _send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """Sends a JSON-RPC 2.0 notification (fire-and-forget, no id)."""
        if not self.is_running or not self.process or not self.process.stdin:
            return

        notif = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }
        msg_bytes = (json.dumps(notif) + "\n").encode("utf-8")
        self.process.stdin.write(msg_bytes)
        await self.process.stdin.drain()

    async def _initialize(self) -> bool:
        """Executes the standard MCP initialization handshake."""
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": False},
                "sampling": {},
            },
            "clientInfo": {
                "name": "SovereignOS-MCP-Client",
                "version": "2.0.0",
            },
        }

        result = await self._send_request("initialize", init_params)
        self.server_info = result.get("serverInfo", {})
        self.capabilities = result.get("capabilities", {})

        # Send initialized notification
        await self._send_notification("notifications/initialized")
        return True

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Queries the server for all registered tools via tools/list."""
        res = await self._send_request("tools/list", {})
        self.discovered_tools = res.get("tools", [])
        return self.discovered_tools

    async def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a specific tool via tools/call."""
        params = {
            "name": tool_name,
            "arguments": arguments or {},
        }
        res = await self._send_request("tools/call", params)
        return res

    async def close(self):
        """Closes the connection and terminates the subprocess."""
        if self._reader_task:
            self._reader_task.cancel()
            self._reader_task = None

        for fut in self._pending_requests.values():
            if not fut.done():
                fut.cancel()
        self._pending_requests.clear()

        if self.process:
            try:
                if self.process.stdin:
                    self.process.stdin.close()
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=3.0)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            finally:
                self.process = None

        self._is_initialized = False
        logger.info(f"MCP server '{self.name}' closed.")
