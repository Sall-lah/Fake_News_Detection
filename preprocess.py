import re

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

__all__ = ["clean_text"]


def clean_text(title: str | None, text: str | None) -> str:
    """Combine and clean input text deterministically."""
    safe_title = title or ""
    safe_text = text or ""
    combined = f"{safe_title} {safe_text}".lower()
    cleaned = re.sub(r"[^a-z]", " ", combined)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        return ""

    tokens = cleaned.split(" ")
    deduped_tokens: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token in ENGLISH_STOP_WORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        deduped_tokens.append(token)

    final_text = " ".join(deduped_tokens)
    final_text = re.sub(r"\s+", " ", final_text).strip()
    return final_text
