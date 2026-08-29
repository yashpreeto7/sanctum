# Research & Findings Log

## System Setup & Execution Protocol
- **Non-Interactive Execution:** PowerShell / Bash commands must run without interactive pagers (`$env:PAGER='cat'`) or waiting prompts.
- **Background Processes:** Server (`run_server.py`) and UI (`launch_desktop_app.py`) require daemon/async handling when tested.
- **Context Preservation:** In-progress work and status are written to `task_plan.md` and `progress.md` before and after major steps.
