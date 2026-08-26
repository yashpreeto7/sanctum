# Directive: Continuous Evaluation, Evals & Benchmarks

## Goal
Quantitatively measure retrieval accuracy, agent trajectory fidelity, and indirect prompt injection defenses on every release to ensure enterprise-grade reliability and zero hallucinated tool executions.

## Benchmark Matrix & Target Metrics

| Evaluation Domain | Metric | Target SLA | Benchmark Script |
| :--- | :--- | :--- | :--- |
| **Hybrid RAG Retrieval** | **HitRate@3** | $\ge 80\%$ | `tests/evals/test_rag_eval.py` |
| **Hybrid RAG Retrieval** | **MRR (Mean Reciprocal Rank)** | $\ge 0.70$ | `tests/evals/test_rag_eval.py` |
| **Security Quarantine** | **Threat Interception Rate** | **100%** | `tests/evals/test_security_quarantine.py` |
| **Security Quarantine** | **False Positive Rate** | $0.0\%$ | `tests/evals/test_security_quarantine.py` |
| **Agent Trajectories** | **HITL Gate Activation** | **100% on High-Risk** | `tests/evals/test_agent_trajectories.py` |
| **ML Gatekeeper** | **Inference Latency** | $< 10\text{ms}$ on CPU | `tests/unit/test_triaging_classifier.py` |

## Running Full Test & Eval Suite
```bash
# Run all unit tests
.venv/Scripts/pytest tests/unit/ -v

# Run API integration tests
.venv/Scripts/pytest tests/integration/ -v

# Run comprehensive quantitative benchmarks & red-teaming
.venv/Scripts/pytest tests/evals/ -v
```
