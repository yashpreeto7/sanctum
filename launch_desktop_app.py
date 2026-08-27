"""Desktop Application Launcher for Personal AI OS.

Launches the Personal AI OS Command Center in a dedicated native desktop window.
Supports pywebview with automatic fallback to native Chromium/Edge App Mode.
"""

import os
import sys
import time
import socket
import subprocess
import threading
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PORT = 8000
APP_URL = f"http://127.0.0.1:{PORT}"
APP_TITLE = "Personal AI OS — Operations Dashboard"


def is_server_running(port: int = PORT) -> bool:
    """Check if the local FastAPI server is listening on port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def get_python_exe() -> str:
    """Find the best python executable (preferring local .venv)."""
    venv_py = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def start_backend_server():
    """Starts the uvicorn backend server in the background if not already alive."""
    if is_server_running(PORT):
        print(f"[Desktop App] Backend server already running on {APP_URL}")
        return None

    py_exe = get_python_exe()
    print(f"[Desktop App] Starting Personal AI OS backend server on {APP_URL} using {py_exe}...")
    cmd = [py_exe, "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1", "--port", str(PORT)]
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for server to become responsive
    max_retries = 30
    for _ in range(max_retries):
        time.sleep(0.3)
        if is_server_running(PORT):
            print(f"[Desktop App] Backend server is ready at {APP_URL}")
            return proc

    print("[Desktop App] Warning: Server launch timed out, attempting to continue...")
    return proc


def launch_with_pywebview():
    """Attempts to launch a sleek standalone window via pywebview."""
    try:
        import webview
        print("[Desktop App] Launching standalone window via pywebview...")
        window = webview.create_window(
            title=APP_TITLE,
            url=APP_URL,
            width=1440,
            height=900,
            min_size=(900, 600),
            background_color="#090a0f",
            text_select=True,
            confirm_close=False,
        )
        webview.start(debug=False)
        return True
    except Exception as exc:
        print(f"[Desktop App] pywebview launch failed ({exc}). Falling back to Native App Mode...")
        return False


def launch_with_native_app_mode():
    """Fallback: Launches standalone chromeless app window via Edge or Chrome."""
    print("[Desktop App] Launching standalone app mode via native browser engine...")

    # Candidate browser executables on Windows
    edge_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]
    chrome_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]

    for p in edge_paths + chrome_paths:
        if os.path.exists(p):
            args = [
                p,
                f"--app={APP_URL}",
                "--window-size=1440,900",
                "--app-auto-launched",
                f"--app-id=personal_ai_os_{PORT}",
            ]
            print(f"[Desktop App] Launching chromeless desktop window using: {p}")
            subprocess.Popen(args)
            return True

    # Final fallback: default web browser
    import webbrowser
    print("[Desktop App] Opening in default web browser...")
    webbrowser.open(APP_URL)
    return True


def main():
    server_proc = start_backend_server()
    time.sleep(0.5)

    # First try pywebview
    success = launch_with_pywebview()
    if not success:
        launch_with_native_app_mode()

    if server_proc:
        try:
            server_proc.wait()
        except KeyboardInterrupt:
            server_proc.terminate()


if __name__ == "__main__":
    main()
