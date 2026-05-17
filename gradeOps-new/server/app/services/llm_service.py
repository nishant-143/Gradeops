import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from anthropic import Anthropic
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)


PROVIDER_ALIASES = {
    "chatgpt": "openai",
    "openai": "openai",
    "claude": "anthropic",
    "anthropic": "anthropic",
    "grok": "xai",
    "xai": "xai",
}


def normalize_provider(raw: str) -> str:
    key = (raw or "").strip().lower()
    return PROVIDER_ALIASES.get(key, key)


@dataclass
class ProviderConfig:
    provider: str
    model: str
    api_key: str
    base_url: str | None = None


class LLMService:
    def __init__(self) -> None:
        fallback = [normalize_provider(v.strip()) for v in settings.LLM_FALLBACK_ORDER.split(",") if v.strip()]
        self._providers = []
        for provider in fallback:
            cfg = self._build_provider_config(provider)
            if cfg:
                self._providers.append(cfg)

        primary = self._build_provider_config(normalize_provider(settings.LLM_PROVIDER))
        if primary and all(primary.provider != p.provider for p in self._providers):
            self._providers.insert(0, primary)

    @staticmethod
    def _build_provider_config(provider: str) -> ProviderConfig | None:
        if provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                return None
            return ProviderConfig(
                provider="anthropic",
                model=settings.LLM_MODEL or settings.ANTHROPIC_MODEL,
                api_key=settings.ANTHROPIC_API_KEY,
            )
        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                return None
            return ProviderConfig(
                provider="openai",
                model=settings.LLM_MODEL or settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
            )
        if provider == "xai":
            if not settings.XAI_API_KEY:
                return None
            return ProviderConfig(
                provider="xai",
                model=settings.LLM_MODEL or settings.XAI_MODEL,
                api_key=settings.XAI_API_KEY,
                base_url=settings.XAI_BASE_URL,
            )
        return None

    def invoke_json(self, prompt: str, trace: Dict[str, Any]) -> Dict[str, Any]:
        if not self._providers:
            raise RuntimeError("No configured LLM provider credentials found")

        errors: List[str] = []
        for cfg in self._providers:
            try:
                logger.info("llm.request provider=%s trace=%s", cfg.provider, trace)
                raw = self._invoke_provider(cfg, prompt)
                return self._parse_json(raw)
            except Exception as exc:
                msg = f"{cfg.provider}: {exc}"
                errors.append(msg)
                logger.warning("llm.provider_failed provider=%s error=%s", cfg.provider, exc)
        raise RuntimeError(f"All providers failed: {' | '.join(errors)}")

    @retry(stop=stop_after_attempt(settings.LLM_MAX_RETRIES), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _invoke_provider(self, cfg: ProviderConfig, prompt: str) -> str:
        timeout = settings.LLM_REQUEST_TIMEOUT_SECONDS
        if cfg.provider == "anthropic":
            client = Anthropic(api_key=cfg.api_key, timeout=timeout)
            res = client.messages.create(
                model=cfg.model,
                max_tokens=2000,
                temperature=settings.LLM_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(block.text for block in res.content if getattr(block, "type", "") == "text")

        client_kwargs: Dict[str, Any] = {"api_key": cfg.api_key, "timeout": timeout}
        if cfg.base_url:
            client_kwargs["base_url"] = cfg.base_url
        client = OpenAI(**client_kwargs)
        res = client.chat.completions.create(
            model=cfg.model,
            temperature=settings.LLM_TEMPERATURE,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        return (res.choices[0].message.content or "").strip()

    @staticmethod
    def _parse_json(raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                return json.loads(raw[start : end + 1])
            raise


llm_service = LLMService()
