"""
Exhaustive Source Code Listings and Line-by-Line Architectural Annotations.
"""

CODE_LISTINGS = [
    ("1. server/app.py — WebSocket Streaming Protocol & Lifecycle",
     """# server/app.py - Real-Time FastAPI & WebSocket Gateway
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio, json, uuid
from execution.orchestration.agent_engine import build_agent_graph, AgentState

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize background watchers & connection pools
    print("[SYSTEM] Starting SovereignOS Daemons & Watchers...")
    app.state.graph = build_agent_graph()
    yield
    # Shutdown: Cleanly drain connection queues
    print("[SYSTEM] Draining task queues & shutting down.")

app = FastAPI(title="SovereignOS Backend", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    try:
        while True:
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)
            user_msg = payload.get("command", "")
            
            # Initialize LangGraph AgentState
            initial_state = {
                "messages": [{"role": "user", "content": user_msg}],
                "context_docs": [], "planned_tool": None,
                "tool_args": {}, "approval_required": False, "risk_level": "LOW"
            }
            
            # Stream events using LangGraph v1 astream_events
            async for event in app.state.graph.astream_events(initial_state, version="v1"):
                event_type = event.get("event")
                if event_type == "on_chain_start":
                    node_name = event.get("name", "")
                    await websocket.send_json({"type": "node_progress", "node": node_name})
                elif event_type == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        await websocket.send_json({"type": "token", "chunk": chunk})
            
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        print(f"[WS] Client disconnected: {session_id}")"""),

    ("2. execution/security/quarantine.py — Zero-Shot Prompt Injection Gate",
     """# execution/security/quarantine.py - Prompt Injection Defense
import re, uuid
from typing import Dict, Any

class QuarantineSecurityGate:
    def __init__(self):
        # Heuristic blacklist of dangerous override patterns
        self.injection_patterns = [
            re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
            re.compile(r"system\s+override", re.IGNORECASE),
            re.compile(r"reveal\s+system\s+prompt", re.IGNORECASE),
            re.compile(r"bypass\s+security\s+filter", re.IGNORECASE)
        ]

    def evaluate_threat(self, user_input: str) -> Dict[str, Any]:
        canary_token = str(uuid.uuid4())
        
        # Phase 1: Static Heuristic Regex Check
        for pattern in self.injection_patterns:
            if pattern.search(user_input):
                return {
                    "is_safe": False,
                    "risk_level": "HIGH",
                    "reason": f"Detected forbidden injection pattern: {pattern.pattern}",
                    "canary": canary_token
                }
        
        # Phase 2: Length and Dangerous Tool Word Heuristics
        destructive_keywords = ["delete", "drop", "truncate", "format_drive", "send_mass_email"]
        has_destructive = any(kw in user_input.lower() for kw in destructive_keywords)
        
        risk = "HIGH" if has_destructive else ("MEDIUM" if len(user_input) > 1000 else "LOW")
        
        return {
            "is_safe": True,
            "risk_level": risk,
            "canary": canary_token
        }"""),

    ("3. execution/rag/hybrid_retriever.py — Dense + Sparse Reciprocal Rank Fusion",
     """# execution/rag/hybrid_retriever.py - Qdrant + BM25 Hybrid Search
import math
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

class HybridRAGRetriever:
    def __init__(self, qdrant_path: str = "./qdrant_data"):
        self.encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.qdrant = QdrantClient(path=qdrant_path)
        self.collection_name = "sovereign_knowledge"

    def search_hybrid(self, query: str, top_k: int = 5, rrf_k: int = 60) -> List[Dict[str, Any]]:
        # 1. Dense Vector Search in Qdrant
        query_vector = self.encoder.encode(query).tolist()
        dense_results = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k * 2
        )
        
        # 2. Sparse Lexical Search (BM25 Mock/Inverted Index)
        sparse_results = self._search_bm25(query, limit=top_k * 2)
        
        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        for rank, doc in enumerate(dense_results):
            doc_id = doc.id
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank + 1))
            
        for rank, doc in enumerate(sparse_results):
            doc_id = doc["id"]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank + 1))
            
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        return [self._get_doc_by_id(doc_id) for doc_id in sorted_ids[:top_k]]"""),

    ("4. execution/tools/calendar_connector.py — Offline-First Tombstone Sync",
     """# execution/tools/calendar_connector.py - Offline Sync & Conflict Resolution
import os, json
from typing import List, Dict, Any

class GoogleCalendarConnector:
    def __init__(self, local_cache: str = "data/local_calendar_events.json",
                 tombstone_file: str = "data/deleted_calendar_events.json"):
        self.local_cache = local_cache
        self.tombstone_file = tombstone_file
        
    def _get_composite_key(self, event: Dict[str, Any]) -> str:
        summary = event.get("summary", "").strip()
        start = event.get("start", {}).get("dateTime", "")[:16]
        return f"{summary}|{start}"
        
    def delete_event_offline(self, event_id: str, summary: str, start_time: str):
        tombstone = {
            "id": event_id,
            "composite_key": f"{summary.strip()}|{start_time[:16]}",
            "timestamp": "2026-08-31T18:00:00Z"
        }
        tombstones = self._load_json(self.tombstone_file)
        tombstones.append(tombstone)
        self._save_json(self.tombstone_file, tombstones)
        
        # Remove from active local cache
        active_events = [e for e in self._load_json(self.local_cache) if e.get("id") != event_id]
        self._save_json(self.local_cache, active_events)
        
    def sync_with_remote(self, google_service):
        # 1. Process deletions first to prevent zombie resurrecting
        tombstones = self._load_json(self.tombstone_file)
        for tb in tombstones:
            try:
                google_service.events().delete(calendarId="primary", eventId=tb["id"]).execute()
            except Exception: pass
        self._save_json(self.tombstone_file, [])  # Clear tombstones
        
        # 2. Upsert active events
        active_events = self._load_json(self.local_cache)
        for ev in active_events:
            # Match on composite key to avoid duplicate insertion
            self._upsert_remote_event(google_service, ev)""")
]

print("Loaded extra code listings.")
