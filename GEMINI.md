# Workspace Execution Rules & Anti-Cancellation Protocol

## 1. Automated Access & Execution
- **Automated Access Granted**: Execute all terminal commands, scripts, file edits, and MCP tool operations directly and autonomously without waiting or prompting for permission.
- **Proactive Execution**: Immediately run tools, start background servers when needed, and resolve issues without manual confirmation prompts.

## 2. Robust Command Execution (Prevent Timeouts & Cancellations)
- **Non-Interactive Execution**: Always pass non-interactive flags to CLI commands (e.g. `uv pip install -y`, `npm install --yes`, `git --no-pager`, `pytest -q`).
- **Paging & Output Control**: Always ensure `$env:PAGER='cat'` or equivalent is set so commands never hang on pagination prompts (`less`/`more`).
- **Async & Background Handling**: For long-running servers, listeners, or watchers, always launch them as daemons (`IsDaemon: true`) so they do not block tool execution loops.
- **Error Trapping**: Always inspect return codes and standard error before concluding. Never loop endlessly on broken synchronous commands.

## 3. Persistent Context & Anti-Context-Loss Architecture
- **Manus-Style Working Memory on Disk**: Maintain `task_plan.md`, `findings.md`, and `progress.md` in the workspace root at all times.
- **2-Action Logging Rule**: After every 2 major observations or phase completions, write state and discoveries to disk so context survives `/clear` and session resets.
- **Reboot Protocol**: At session start or recovery, re-read `task_plan.md` and `progress.md` to resume exactly where the workflow left off without losing state.
- **Cross-Session Memory**: Sync architectural decisions and persistent facts to `claude-mem` MCP.
