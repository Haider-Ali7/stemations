"""
Shared model IDs and fallback order for Google GenAI (Gemini API).
Gemma 4 may return transient 500 errors on some keys; Gemini 3.x is the reliable fallback.
"""

# User-facing options (frontend model selector)
AVAILABLE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemma-4-26b-a4b-it",
    "gemini-3.8-flash",
    "gemini-3-flash-preview",
    "gemma-4-31b-it",
]

DEFAULT_MODEL = "gemini-3.5-flash-lite"

# Reliable fallbacks when the selected model fails
GENERATION_FALLBACKS = [
    "gemini-3.5-flash-lite",
    "gemma-4-26b-a4b-it",
    "gemini-3.8-flash",
    "gemini-3-flash-preview",
    "gemma-4-31b-it",
]

SELF_HEAL_FALLBACKS = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemma-4-26b-a4b-it",
]


def model_attempt_order(primary: str, fallbacks: list[str]) -> list[str]:
    """Primary first, then fallbacks, without duplicates."""
    ordered: list[str] = []
    for name in [primary, *fallbacks]:
        if name and name not in ordered:
            ordered.append(name)
    return ordered
