"""
Personal AI OS — Native Desktop Window Launcher.
Launches the Personal AI OS Command Center in a borderless, native app-mode desktop window.
"""
import os
import sys
import time
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PORT = 8000
APP_URL = f"http://127.0.0.1:{PORT}"

def is_server_running(url: str) -> bool:
    """Check if the backend server is accepting HTTP requests."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Personal-AI-OS-Launcher"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False

def find_browser_binary() -> str:
    """Finds Google Chrome, Microsoft Edge, or Brave executable on Windows."""
    candidates = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # Fallback to PATH
    for name in ["chrome", "msedge", "brave"]:
        found = shutil.which(name)
        if found:
            return found
    return ""

def main():
    print("=" * 60)
    print("  🚀 Starting Personal AI OS — Desktop Command Center")
    print("=" * 60)

    server_process = None
    if not is_server_running(APP_URL):
        print(f"[*] Booting local uvicorn server at {APP_URL}...")
        python_exe = sys.executable
        server_process = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1", "--port", str(PORT)],
            cwd=str(ROOT_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Wait for server to become ready
        for _ in range(25):
            if is_server_running(APP_URL):
                print("[+] Backend server is LIVE!")
                break
            time.sleep(0.4)
    else:
        print("[+] Backend server already running on port 8000.")

    browser_exe = find_browser_binary()
    if browser_exe:
        print(f"[*] Spawning native app window via {os.path.basename(browser_exe)}...")
        user_data_dir = ROOT_DIR / ".desktop_profile"
        user_data_dir.mkdir(exist_ok=True)
        
        flags = [
            browser_exe,
            f"--app={APP_URL}",
            f"--user-data-dir={str(user_data_dir)}",
            "--window-size=1400,900",
            "--window-position=100,50",
            "--disable-extensions",
            "--disable-plugins",
        ]
        try:
            subprocess.run(flags)
        except KeyboardInterrupt:
            pass
    else:
        print(f"[!] Browser binary not found. Opening default web browser at {APP_URL}...")
        import webbrowser
        webbrowser.open(APP_URL)

    if server_process:
        print("[*] Terminating background server process...")
        server_process.terminate()

if __name__ == "__main__":
    main()
