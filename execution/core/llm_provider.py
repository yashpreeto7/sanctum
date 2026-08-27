"""Unified Local LLM Provider interface supporting Ollama and structured Pydantic outputs."""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError

from execution.core.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMResponse(BaseModel):
    """Standardized response container for LLM generation."""

    content: str
    model: str
    latency_ms: float
    total_tokens: Optional[int] = None
    structured_data: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Generate text response from the model."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        schema: Type[T],
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 2,
    ) -> T:
        """Generate structured output validated against a Pydantic schema."""
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Stream token chunks asynchronously."""
        pass

    async def is_available(self) -> bool:
        """Check if the provider backend is available."""
        return True


class OllamaProvider(BaseLLMProvider):
    """Local LLM Provider backed by an Ollama instance."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.default_model = default_model or settings.DEFAULT_REASONING_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

    async def is_available(self) -> bool:
        """Check if local Ollama daemon is running."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        target_model = model or self.default_model
        temp = temperature if temperature is not None else settings.LLM_TEMPERATURE

        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temp},
        }
        if system_prompt:
            payload["system"] = system_prompt

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(f"{self.base_url}/api/generate", json=payload)
            res.raise_for_status()
            data = res.json()

        latency = (time.perf_counter() - start_time) * 1000.0
        total_tokens = data.get("eval_count")

        return LLMResponse(
            content=data.get("response", ""),
            model=target_model,
            latency_ms=latency,
            total_tokens=total_tokens,
        )

    async def generate_structured(
        self,
        schema: Type[T],
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 2,
    ) -> T:
        """Enforces Pydantic schema validation using JSON mode and self-healing retries."""
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        base_system = (
            f"{system_prompt or ''}\n\n"
            f"You MUST output valid JSON strictly conforming to this JSON Schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"Do not include any explanation or markdown formatting outside the raw JSON object."
        ).strip()

        target_model = model or self.default_model
        current_prompt = prompt

        for attempt in range(max_retries + 1):
            payload = {
                "model": target_model,
                "prompt": current_prompt,
                "system": base_system,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.0},
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                res.raise_for_status()
                data = res.json()

            raw_text = data.get("response", "").strip()

            try:
                parsed_dict = json.loads(raw_text)
                return schema.model_validate(parsed_dict)
            except (json.JSONDecodeError, ValidationError) as err:
                if attempt == max_retries:
                    raise ValueError(
                        f"Failed to generate valid structured output for {schema.__name__} after {max_retries + 1} attempts. Last error: {err}. Raw output: {raw_text}"
                    ) from err
                current_prompt = (
                    f"{prompt}\n\n"
                    f"Previous attempt produced invalid JSON/schema error:\n{err}\n"
                    f"Please fix and output valid JSON conforming strictly to schema."
                )

        raise RuntimeError("Unexpected failure in generate_structured loop.")

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncIterator[str]:
        target_model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": settings.LLM_TEMPERATURE},
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/generate", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    chunk_data = json.loads(line)
                    yield chunk_data.get("response", "")


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock provider for unit testing without a live Ollama daemon."""

    def __init__(self, canned_response: str = '{"status": "ok"}'):
        self.canned_response = canned_response

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        return LLMResponse(
            content=self.canned_response,
            model="mock-model",
            latency_ms=1.5,
            total_tokens=10,
        )

    async def generate_structured(
        self,
        schema: Type[T],
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 2,
    ) -> T:
        try:
            data = json.loads(self.canned_response)
            return schema.model_validate(data)
        except Exception:
            raise ValueError(f"Mock response does not match schema {schema.__name__}")

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncIterator[str]:
        for word in self.canned_response.split():
            yield word + " "


# Default instance
llm_provider = OllamaProvider()
