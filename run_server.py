import sys
import uvicorn

if __name__ == "__main__":
    print("[Server Runner] Starting Personal AI OS Backend Server...")
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, log_level="info", access_log=True)
