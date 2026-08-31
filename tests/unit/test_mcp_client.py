"""Unit tests for Universal Model Context Protocol (MCP) Client and Manager."""

import pytest
import asyncio
from pathlib import Path
from execution.tools.mcp_client import MCPClient
from execution.tools.mcp_manager import MCPManager


@pytest.mark.asyncio
async def test_mcp_client_initialization_and_properties():
    """Verify MCPClient object instantiation and properties."""
    client = MCPClient(
        name="test_sqlite",
        command="python",
        args=["-c", "import sys; print('ready'); sys.exit(0)"],
        env={"TEST_VAR": "1"},
        timeout=5.0,
    )
    assert client.name == "test_sqlite"
    assert client.command == "python"
    assert client.timeout == 5.0
    assert not client.is_running
    assert len(client.discovered_tools) == 0


def test_mcp_manager_crud(tmp_path: Path):
    """Verify MCPManager loads configs and handles add/delete."""
    config_file = tmp_path / "mcp_servers.json"
    manager = MCPManager(config_path=config_file)

    # Initial defaults should be loaded
    servers = manager.list_servers_status()
    assert len(servers) >= 4
    names = [s["name"] for s in servers]
    assert "filesystem" in names
    assert "sqlite" in names

    # Add custom server
    asyncio.run(manager.add_or_update_server(
        name="custom_mock",
        config={"command": "echo", "args": ["hello"], "enabled": False, "description": "Mock Echo Server"},
        auto_start=False
    ))

    servers_updated = manager.list_servers_status()
    updated_names = [s["name"] for s in servers_updated]
    assert "custom_mock" in updated_names

    # Delete custom server
    deleted = asyncio.run(manager.delete_server("custom_mock"))
    assert deleted is True

    servers_final = manager.list_servers_status()
    final_names = [s["name"] for s in servers_final]
    assert "custom_mock" not in final_names
