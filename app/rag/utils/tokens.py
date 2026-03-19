"""Token counting and truncation utilities."""

from __future__ import annotations

from functools import lru_cache

import tiktoken


@lru_cache(maxsize=4)
def _get_encoding(model: str = "cl100k_base") -> tiktoken.Encoding:
    return tiktoken.get_encoding(model)


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count the number of tokens in text."""
    enc = _get_encoding(encoding_name)
    return len(enc.encode(text, disallowed_special=()))


def truncate_to_tokens(
    text: str, max_tokens: int, encoding_name: str = "cl100k_base"
) -> str:
    """Truncate text to a maximum number of tokens."""
    enc = _get_encoding(encoding_name)
    tokens = enc.encode(text, disallowed_special=())
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[:max_tokens])
