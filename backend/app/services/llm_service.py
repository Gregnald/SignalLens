"""Pluggable structured-output LLM service.

ARCHITECTURE.md / VIBE_CODING_RULES.md contract:
- Every important LLM call uses a JSON schema and returns a validated Pydantic object.
- On validation failure: retry once with the validation error, otherwise raise LLMGenerationError
  (callers must not silently fabricate a fallback).
- The LLM is NEVER the source of truth for counts/dates/ratings/growth/confidence — callers only
  pass already-computed facts into the prompt.

Providers: gemini | groq | mock, selected by settings.llm_provider.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar("T", bound=BaseModel)


class LLMGenerationError(Exception):
    pass


class LLMProvider(ABC):
    name: str = "unknown"

    @abstractmethod
    def _raw_generate(self, prompt: str, schema: type[BaseModel]) -> str:
        """Return raw JSON text from the model for the given prompt/schema."""

    def generate_structured(self, prompt: str, schema: type[T]) -> T:
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                effective_prompt = prompt
                if attempt == 1 and last_error is not None:
                    effective_prompt = (
                        f"{prompt}\n\nYour previous response was invalid: {last_error}\n"
                        f"Return ONLY valid JSON matching the schema."
                    )
                raw = self._raw_generate(effective_prompt, schema)
                data = json.loads(raw)
                return schema.model_validate(data)
            except (ValidationError, json.JSONDecodeError) as exc:
                last_error = exc
                logger.warning("LLM structured output invalid (attempt %s): %s", attempt + 1, exc)
        raise LLMGenerationError(
            f"LLM provider '{self.name}' failed to produce valid {schema.__name__} after retry: {last_error}"
        )


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self) -> None:
        from google import genai

        if not settings.gemini_api_key:
            raise LLMGenerationError("GEMINI_API_KEY is not set")
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def _raw_generate(self, prompt: str, schema: type[BaseModel]) -> str:
        models_to_try = [settings.gemini_model, settings.gemini_fallback_model]
        last_exc: Exception | None = None
        for model in models_to_try:
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": schema,
                    },
                )
                return response.text
            except Exception as exc:  # noqa: BLE001 - fall back to next model
                last_exc = exc
                logger.warning("Gemini model %s failed: %s", model, exc)
        raise LLMGenerationError(f"All Gemini models failed: {last_exc}")


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self) -> None:
        from groq import Groq

        if not settings.groq_api_key:
            raise LLMGenerationError("GROQ_API_KEY is not set")
        self._client = Groq(api_key=settings.groq_api_key)

    def _raw_generate(self, prompt: str, schema: type[BaseModel]) -> str:
        schema_json = json.dumps(schema.model_json_schema())
        completion = self._client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You output ONLY valid JSON matching this JSON schema, no prose, "
                        f"no markdown fences: {schema_json}"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return completion.choices[0].message.content or "{}"


class MockProvider(LLMProvider):
    """Deterministic, clearly-labeled mock used when no LLM key is configured."""

    name = "mock"

    def _raw_generate(self, prompt: str, schema: type[BaseModel]) -> str:
        mock = _mock_fill(schema)
        return json.dumps(mock)


def _mock_fill(schema: type[BaseModel]) -> dict:
    fields = schema.model_fields
    out: dict = {}
    for field_name, field in fields.items():
        out[field_name] = _mock_value_for(field_name, field.annotation)
    return out


def _mock_value_for(field_name: str, annotation) -> object:
    type_str = str(annotation)
    label = field_name.replace("_", " ")
    if "list" in type_str.lower():
        if "int" in type_str.lower():
            return []
        return [f"[MOCK] example {label} 1", f"[MOCK] example {label} 2"]
    if annotation in (int, float):
        return 0
    if field_name == "severity":
        return "medium"
    if field_name == "priority":
        return "P2"
    if field_name == "category":
        return "Other"
    return f"[MOCK OUTPUT — no LLM_PROVIDER key configured] Placeholder {label}."


_provider_cache: dict[str, LLMProvider] = {}


def get_llm_provider() -> LLMProvider:
    provider_name = settings.llm_provider
    if provider_name in _provider_cache:
        return _provider_cache[provider_name]

    provider: LLMProvider
    try:
        if provider_name == "gemini":
            provider = GeminiProvider()
        elif provider_name == "groq":
            provider = GroqProvider()
        else:
            provider = MockProvider()
    except LLMGenerationError as exc:
        logger.warning("Falling back to mock LLM provider: %s", exc)
        provider = MockProvider()

    _provider_cache[provider_name] = provider
    return provider
