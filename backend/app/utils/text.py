import re
import unicodedata

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def is_empty_review(text: str) -> bool:
    return len(normalize_text(text)) < 2
