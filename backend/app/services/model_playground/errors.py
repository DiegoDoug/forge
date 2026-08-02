from __future__ import annotations

# Maps an SDK exception's class name to a short, user-legible message - never
# the raw exception text or a stack trace (docs/Security.md "Input
# handling"). Every OpenAI-compatible provider (DeepSeek, Kimi, GLM, Gemini,
# Custom) raises the same `openai` SDK exception classes as OpenAI itself,
# so this one mapping covers all of them plus Anthropic without per-provider
# branching (ADR-0013 SS2.1).
_EXCEPTION_MESSAGES: dict[str, str] = {
    "AuthenticationError": "Authentication failed - check the configured API key.",
    "PermissionDeniedError": "The API key does not have permission for this model.",
    "RateLimitError": "Rate limited by the provider - try again shortly.",
    "NotFoundError": "The requested model was not found by the provider.",
    "APIConnectionError": "Could not reach the provider - check network connectivity.",
    "APIStatusError": "The provider returned an error response.",
    "BadRequestError": "The provider rejected the request.",
}


def to_user_message(exc: Exception) -> str:
    return _EXCEPTION_MESSAGES.get(type(exc).__name__, "Request failed.")
