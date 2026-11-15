"""Multi-provider AI completion client with waterfall failover, telemetry, and JSON extraction."""

import json
import re
import time
from dataclasses import dataclass

import httpx

from .config import Settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

FREE = re.compile(r"^(openrouter/free|[a-z0-9./_-]+:free)$", re.IGNORECASE)
PAID_MODELS = {"qwen/qwen3.7-flash", "openai/gpt-6-luna"}
MAX_TOKENS = 4000
HEADERS = {
    "HTTP-Referer": "https://perpustakaanhati-production.up.railway.app",
    "X-Title": "Perpustakaan Hati Research",
}

DEFAULT_PROVIDER_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "nim": "meta/llama-3.3-70b-instruct",
    "openai_compat": "gpt-4o-mini",
}


class ResearchError(RuntimeError):
    """Sanitized provider or validation failure."""


def strip_em_dashes(text: str) -> str:
    """Replace typographic em/en dashes cleanly in generated brand copy."""
    return str(text or "").replace("—", ",").replace("–", "-")


def strip_em_dashes_deep(value):
    if isinstance(value, str):
        return strip_em_dashes(value)
    if isinstance(value, list):
        return [strip_em_dashes_deep(item) for item in value]
    if isinstance(value, dict):
        return {k: strip_em_dashes_deep(v) for k, v in value.items()}
    return value


def is_free_model(model: str) -> bool:
    return bool(FREE.search(model))


def resolve_openrouter_model(settings: Settings) -> str:
    if not settings.openrouter_api_key:
        raise ResearchError("OPENROUTER_API_KEY is not set. Add it to the environment and retry.")
    model = settings.openrouter_model
    allowed = PAID_MODELS | set(getattr(settings, "allowed_models", ()) or ())
    if model not in allowed and not FREE.search(model):
        raise ResearchError(
            f"Model '{model}' is not allowlisted. Use a free model, or add it to PAID_MODELS if it is worth paying for."
        )
    return model


def build_openrouter_payload(model: str, system: str, user: str, *, max_tokens: int = MAX_TOKENS) -> dict:
    """Build an OpenRouter request payload compatible with free and paid reasoning models."""
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_object"},
        "reasoning": {"enabled": False},
        "max_completion_tokens" if model.startswith("openai/") else "max_tokens": max_tokens,
    }
    if is_free_model(model):
        payload["provider"] = {"max_price": {"prompt": 0, "completion": 0}}
    return payload


def openrouter_headers(settings: Settings) -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.openrouter_api_key}", **HEADERS}


def openrouter_http_failure(status_code: int) -> ResearchError:
    if status_code == 429:
        return ResearchError("OpenRouter rate limit reached; retry later.")
    if status_code == 404:
        return ResearchError(
            "OpenRouter found no endpoint for the configured model (HTTP 404). "
            "Check OPENROUTER_MODEL, and that a provider still serves it, then retry."
        )
    return ResearchError(f"OpenRouter error (HTTP {status_code}); check the API key and retry.")


def content_text(content) -> str:
    """Normalise string or structured multi-part chat content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [part["text"] for part in content if isinstance(part, dict) and isinstance(part.get("text"), str)]
        return "".join(parts)
    return ""


def parse_json_body(text: str):
    fenced = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
    whole = fenced.group(1).strip() if fenced else text.strip()
    embedded = re.search(r"\{.*\}", text, re.DOTALL)
    for candidate in (whole, embedded.group(0) if embedded else ""):
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except ValueError:
            continue
    raise ResearchError("AI provider returned malformed JSON; retry the research run.")


def extract_json_object(content, *, list_key: str = "insights", finish_reason: str = "") -> dict:
    text = content_text(content)
    if not text.strip():
        if finish_reason == "length":
            raise ResearchError(
                "The AI provider spent its whole output budget before answering, which is what a reasoning model does with no room left for JSON. "
                "Retry, or set OPENROUTER_MODEL to a model that answers directly."
            )
        raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.")
    payload = parse_json_body(text)
    if isinstance(payload, list):
        if not payload:
            raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.")
        payload = {list_key: payload}
    if not isinstance(payload, dict) or not isinstance(payload.get(list_key), list):
        raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.")
    return payload


@dataclass(frozen=True)
class ProviderTarget:
    name: str
    url: str
    api_key: str
    model: str
    is_openrouter: bool = False


def configured_providers(settings: Settings) -> list[ProviderTarget]:
    """Return active AI providers in configured priority order."""
    targets: list[ProviderTarget] = []
    for name in getattr(settings, "ai_provider_priority", ("openrouter", "groq", "nim", "openai_compat")):
        key = name.strip().lower()
        if key == "openrouter" and settings.openrouter_api_key:
            targets.append(
                ProviderTarget(
                    name="openrouter",
                    url=OPENROUTER_URL,
                    api_key=settings.openrouter_api_key,
                    model=resolve_openrouter_model(settings),
                    is_openrouter=True,
                )
            )
        elif key == "groq" and getattr(settings, "groq_api_key", ""):
            targets.append(
                ProviderTarget(
                    name="groq",
                    url=GROQ_URL,
                    api_key=settings.groq_api_key,
                    model=DEFAULT_PROVIDER_MODELS["groq"],
                )
            )
        elif key == "nim" and getattr(settings, "nim_api_key", ""):
            targets.append(
                ProviderTarget(
                    name="nim",
                    url=NIM_URL,
                    api_key=settings.nim_api_key,
                    model=DEFAULT_PROVIDER_MODELS["nim"],
                )
            )
        elif key == "openai_compat" and getattr(settings, "openai_compat_base_url", ""):
            base = settings.openai_compat_base_url.rstrip("/")
            url = base if base.endswith("/chat/completions") else f"{base}/chat/completions"
            targets.append(
                ProviderTarget(
                    name="openai_compat",
                    url=url,
                    api_key=getattr(settings, "openai_compat_api_key", "") or "sk-local",
                    model=DEFAULT_PROVIDER_MODELS["openai_compat"],
                )
            )
    if not targets:
        # Triggers standard OPENROUTER_API_KEY error message cleanly.
        resolve_openrouter_model(settings)
    return targets


def _call_provider(
    target: ProviderTarget,
    system: str,
    user: str,
    http: httpx.Client,
    *,
    max_tokens: int = MAX_TOKENS,
) -> tuple[str, str, dict]:
    if target.is_openrouter:
        payload = build_openrouter_payload(target.model, system, user, max_tokens=max_tokens)
        headers = {"Authorization": f"Bearer {target.api_key}", **HEADERS}
    else:
        payload = {
            "model": target.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
        }
        headers = {"Authorization": f"Bearer {target.api_key}"}

    try:
        response = http.post(target.url, headers=headers, json=payload)
    except httpx.HTTPError:
        label = "OpenRouter" if target.is_openrouter else target.name
        raise ResearchError(f"Could not reach {label}; check your connection and retry.") from None

    if not response.is_success:
        if target.is_openrouter:
            raise openrouter_http_failure(response.status_code)
        raise ResearchError(f"{target.name} error (HTTP {response.status_code}); retry later.")

    try:
        body = response.json()
        choice = body["choices"][0]
        raw_content = choice["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.") from None

    usage = body.get("usage") if isinstance(body, dict) and isinstance(body.get("usage"), dict) else {}
    return raw_content, str(choice.get("finish_reason") or ""), usage


def complete_json(
    settings: Settings,
    http: httpx.Client,
    prompts: tuple[str, str],
    options: dict | None = None,
) -> tuple[dict, dict]:
    """Execute completion across configured provider waterfall and extract JSON."""
    system, user = prompts
    opts = options or {}
    list_key = str(opts.get("list_key", "insights"))
    max_tokens = int(opts.get("max_tokens", MAX_TOKENS))
    operation = str(opts.get("operation", list_key))
    store = opts.get("store")

    targets = configured_providers(settings)
    last_error: ResearchError | None = None
    for idx, target in enumerate(targets):
        t0 = time.monotonic()
        try:
            raw_content, finish_reason, usage = _call_provider(target, system, user, http, max_tokens=max_tokens)
            parsed = extract_json_object(raw_content, list_key=list_key, finish_reason=finish_reason)
            elapsed = int((time.monotonic() - t0) * 1000)
            if store is not None:
                store.record_ai_usage(
                    target.name,
                    target.model,
                    operation,
                    {
                        "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
                        "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
                        "duration_ms": elapsed,
                        "ok": True,
                    },
                )
            return parsed, {"provider": target.name, "model": target.model, "duration_ms": elapsed, "usage": usage}
        except ResearchError as exc:
            last_error = exc
            elapsed = int((time.monotonic() - t0) * 1000)
            if store is not None:
                store.record_ai_usage(
                    target.name,
                    target.model,
                    operation,
                    {"duration_ms": elapsed, "ok": False, "error": str(exc)},
                )
            # Only fail over if another configured provider remains.
            if idx + 1 < len(targets):
                continue
            raise
    assert last_error is not None
    raise last_error
