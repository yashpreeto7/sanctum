import time
import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, path, method="GET", body=None):
    t0 = time.perf_counter()
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            content = resp.read().decode("utf-8")
            print(f"[OK] {name:30} [{method:4} {path:40}] -> {resp.status} in {elapsed_ms:6.2f}ms")
            return content
    except Exception as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        print(f"[ERR] {name:30} [{method:4} {path:40}] -> ERROR ({str(e)}) in {elapsed_ms:6.2f}ms")
        return None

if __name__ == "__main__":
    print("\n" + "="*85)
    print("PERSONAL AI OS -- PERFORMANCE & HEALTH BENCHMARK SUITE")
    print("="*85 + "\n")
    
    test_endpoint("Dashboard Root Page", "/")
    test_endpoint("Inbox Stream", "/api/inbox")
    test_endpoint("Sent Emails Stream", "/api/inbox/sent")
    test_endpoint("LangSmith Execution Traces", "/api/traces")
    test_endpoint("Trace Analytics Stats", "/api/traces/stats")
    test_endpoint("HITL Pending Approvals", "/api/approvals")
    test_endpoint("HITL Policies", "/api/approvals/policies")
    test_endpoint("Calendar Upcoming Events", "/api/calendar/events?days_back=120&days_ahead=365&include_festivals=true")
    test_endpoint("Calendar Cultural Festivals", "/api/calendar/festivals")
    test_endpoint("Obsidian Vault Status", "/api/obsidian/status")
    test_endpoint("Obsidian Notes List", "/api/obsidian/notes")
    test_endpoint(
        "HITL Fast Simulation",
        "/api/approvals/simulate",
        method="POST",
        body={
            "action_type": "send_email",
            "risk_level": "HIGH",
            "target": "sarah@techcorp.io",
            "details": "Urgent wire transfer confirmation",
        },
    )
    
    print("\n" + "="*85)
    print("ALL ENDPOINT BENCHMARKS COMPLETED")
    print("="*85 + "\n")
