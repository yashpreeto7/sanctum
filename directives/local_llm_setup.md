# Directive: Local LLM Configuration & Setup

## Goal
Establish a reliable, local-first inference layer powered by Ollama (Qwen 2.5 7B / Llama 3.2) with strict schema adherence and zero external inference costs.

## Prerequisites
1. **Ollama Installed & Running**:
   - Download: https://ollama.com
   - Start daemon: `ollama serve` (default: `http://localhost:11434`)
2. **Recommended Local Models**:
   - Primary Reasoning Model: `ollama pull qwen2.5:7b` (recommended balance of reasoning, structured output, and speed)
   - Lightweight / Fast Model: `ollama pull qwen2.5:1.5b` or `ollama pull llama3.2:3b`
   - Embedding Model: `all-MiniLM-L6-v2` (via `sentence-transformers` locally)

## Scripts & Tools
- **Provider Interface**: `execution/core/llm_provider.py`
  - `generate(prompt, system_prompt)`: Raw text completion with latency and token metrics.
  - `generate_structured(schema, prompt)`: Schema-enforced JSON extraction using Pydantic validation with self-healing retry loop.
  - `stream(prompt)`: Asynchronous token generator for real-time frontend streaming.

## Configuration Parameters (`.env` or `config.py`)
```env
OLLAMA_BASE_URL="http://localhost:11434"
DEFAULT_REASONING_MODEL="qwen2.5:7b"
DEFAULT_FAST_MODEL="qwen2.5:1.5b"
LLM_TEMPERATURE=0.1
LLM_TIMEOUT_SECONDS=60.0
```

## Error Handling & Self-Annealing Loop
1. **Ollama Daemon Unreachable**:
   - Symptoms: `httpx.ConnectError` to `localhost:11434`.
   - Action: `llm_provider.is_available()` returns `False`. Fall back to diagnostic instructions or mock mode in test environments.
2. **Schema Validation Failure**:
   - If the model emits malformed JSON, `generate_structured` automatically catches `ValidationError` and retries up to `max_retries` times, re-prompting with the exact syntax error diff.
