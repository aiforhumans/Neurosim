"""
Utility functions for NeuroSim.

This module collects a handful of helper functions used across the
project. These include token counting, sentiment analysis, emotion
adjustment and time stamping. Keeping these routines in a single
location allows the agents and UI code to remain focused on higher
level logic.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

try:
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore
    _sentiment_analyser = SentimentIntensityAnalyzer()
except ImportError:  # pragma: no cover - optional dependency
    _sentiment_analyser = None


def num_tokens_from_string(text: str, encoding_name: str = "cl100k_base") -> int:
    """Compute an approximate token count for a given piece of text.

    The token count is dependent on the model encoding being used. If
    the ``tiktoken`` package is installed this function will use it to
    perform an accurate count. Otherwise a simple whitespace-based
    fallback is employed.

    Args:
        text: The text to analyse.
        encoding_name: The name of the encoding to use when counting
            tokens with tiktoken. Defaults to ``cl100k_base`` which is
            appropriate for modern OpenAI chat models.

    Returns:
        An integer representing the number of tokens.
    """
    if tiktoken is not None:
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text))
        except Exception:
            # Fallback to word count if encoding not found
            return len(text.split())
    else:
        # Basic estimate: count words as tokens
        return len(text.split())


def timestamp() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat() + "Z"


def sentiment_score(text: str) -> float:
    """Return a sentiment polarity score in the range [-1, 1].

    If the optional ``vaderSentiment`` dependency is not installed
    this function will return 0. The implementation uses Vader
    sentiment which has been shown to perform well for social media
    style text. Positive values indicate positive sentiment and
    negative values indicate negative sentiment.

    Args:
        text: Input text to analyse.

    Returns:
        A floating point score between -1 and 1.
    """
    if _sentiment_analyser is None:
        return 0.0
    try:
        scores = _sentiment_analyser.polarity_scores(text)
        return float(scores.get("compound", 0.0))
    except Exception:
        return 0.0


def adjust_emotion(
    current: float,
    change: float,
    min_value: float = 0.0,
    max_value: float = 1.0,
) -> float:
    """Apply a change to an emotional value whilst clamping the result.

    Emotional dimensions such as mood and trust are represented as
    floating point values in the range [0, 1]. This helper adjusts
    the current value by a given delta and ensures the result remains
    within the allowed range.

    Args:
        current: The current value of the emotional attribute.
        change: The delta to apply. Positive values increase the
            attribute and negative values decrease it.
        min_value: The minimum allowable value.
        max_value: The maximum allowable value.

    Returns:
        The adjusted emotional value constrained to ``[min_value, max_value]``.
    """
    new_value = current + change
    return max(min(new_value, max_value), min_value)
