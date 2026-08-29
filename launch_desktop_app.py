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
APP_TITLE = "SovereignOS — Autonomous Executive Intelligence"


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
    log_file = ROOT_DIR / ".tmp" / "desktop_server.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_handle = open(log_file, "a", encoding="utf-8")
    cmd = [py_exe, "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1", "--port", str(PORT)]
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT_DIR),
        stdout=log_handle,
        stderr=log_handle,
    )

    # Wait for server to become responsive (allow up to 45s for model warmup)
    max_retries = 90
    for _ in range(max_retries):
        time.sleep(0.5)
        if is_server_running(PORT):
            print(f"[Desktop App] Backend server is ready at {APP_URL}")
            return proc

    print("[Desktop App] Warning: Server launch timed out, attempting to continue...")
    return proc


def launch_with_pywebview():
    """Attempts to launch a sleek standalone window via pywebview with dedicated user data dir."""
    try:
        import webview
        # Set a dedicated isolated user data folder to prevent 0x8007139F lock collisions
        data_dir = ROOT_DIR / ".tmp" / "webview2_profile"
        data_dir.mkdir(parents=True, exist_ok=True)
        os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(data_dir)

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
        print(f"[Desktop App] pywebview failed ({exc}). Launching Native App Mode...")
        return False


def launch_with_native_app_mode():
    """Launches a standalone chromeless native application window via Edge or Chrome."""
    print("[Desktop App] Launching standalone desktop window via native browser app mode...")

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

    profile_dir = ROOT_DIR / ".tmp" / "desktop_app_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    for p in edge_paths + chrome_paths:
        if os.path.exists(p):
            args = [
                p,
                f"--app={APP_URL}",
                f"--user-data-dir={profile_dir}",
                "--window-size=1440,900",
                "--app-auto-launched",
                f"--app-id=personal_ai_os_{PORT}",
                "--enable-features=OverlayScrollbar",
            ]
            print(f"[Desktop App] Launched native standalone window using: {p}")
            proc = subprocess.Popen(args)
            return True

    # Final fallback: default web browser
    import webbrowser
    print("[Desktop App] Opening in default web browser...")
    webbrowser.open(APP_URL)
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Personal AI OS Desktop App Launcher")
    parser.add_argument("--native", action="store_true", help="Directly launch in Native Chromium/Edge App Mode")
    parser.add_argument("--browser", action="store_true", help="Directly open in default web browser")
    args = parser.parse_args()

    server_proc = start_backend_server()
    time.sleep(0.5)

    if args.browser:
        import webbrowser
        webbrowser.open(APP_URL)
    elif args.native:
        launch_with_native_app_mode()
    else:
        # Try native app mode first for best performance and zero-lock reliability, or fallback to pywebview
        launched = launch_with_native_app_mode()
        if not launched:
            launch_with_pywebview()

    if server_proc:
        try:
            server_proc.wait()
        except KeyboardInterrupt:
            server_proc.terminate()


if __name__ == "__main__":
    main()
