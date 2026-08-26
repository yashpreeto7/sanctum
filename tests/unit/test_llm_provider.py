"""Unit tests for the LLM Provider abstraction."""

import pytest
from pydantic import BaseModel, Field
from execution.core.llm_provider import MockLLMProvider, OllamaProvider, LLMResponse


class SampleEmailClassification(BaseModel):
    """Test schema for structured LLM extraction."""

    category: str = Field(..., description="Email category")
    importance_score: float = Field(..., ge=0.0, le=1.0)
    action_required: bool = Field(default=False)
    summary: str = Field(..., description="1-sentence summary")


@pytest.mark.asyncio
async def test_mock_llm_generate():
    """Verify mock provider basic generation."""
    provider = MockLLMProvider(canned_response="Hello world")
    res = await provider.generate("Hi")
    assert isinstance(res, LLMResponse)
    assert res.content == "Hello world"
    assert res.model == "mock-model"
    assert res.latency_ms > 0


@pytest.mark.asyncio
async def test_mock_llm_structured_output():
    """Verify mock provider structured Pydantic extraction."""
    json_payload = (
        '{"category": "work", "importance_score": 0.85, "action_required": true, "summary": "Meeting tomorrow"}'
    )
    provider = MockLLMProvider(canned_response=json_payload)
    data = await provider.generate_structured(
        schema=SampleEmailClassification,
        prompt="Classify this email",
    )
    assert isinstance(data, SampleEmailClassification)
    assert data.category == "work"
    assert data.importance_score == 0.85
    assert data.action_required is True
    assert data.summary == "Meeting tomorrow"


@pytest.mark.asyncio
async def test_mock_llm_streaming():
    """Verify mock provider token stream generator."""
    provider = MockLLMProvider(canned_response="The quick brown fox")
    chunks = []
    async for chunk in provider.stream("Tell me a story"):
        chunks.append(chunk)
    assert "".join(chunks).strip() == "The quick brown fox"


@pytest.mark.asyncio
async def test_ollama_provider_initialization():
    """Verify Ollama provider config attributes."""
    ollama = OllamaProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:7b",
        timeout=30.0,
    )
    assert ollama.base_url == "http://localhost:11434"
    assert ollama.default_model == "qwen2.5:7b"
    assert ollama.timeout == 30.0
