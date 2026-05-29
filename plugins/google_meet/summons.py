# is_summons() — phase 2 wake-word / summons detection for Google Meet.

"""
Determine whether an inbound transcript chunk is a "summons" for Lex
(i.e. TJ explicitly asking Lex to do something) vs. ambient meeting
conversation that should be ignored.

Used by the telegram-meet-callback handler and the action-extractor to
decide whether a wake-word pattern in live captions warrants a reaction.
"""
from __future__ import annotations

import re
from typing import Iterable

# Canonical wake-word / summons patterns.  All matched case-insensitive.
# Each pattern is a (compiled_regex, human_readable_label) tuple.
_SUMMONS_PATTERNS = [
    # Direct address: "Lex, file X" or "Alex, add X"
    (r"\b(Lex|Alex|Lexi|Alexa)\b[^.!?]{0,50}\b(file|add|create|capture|note|record|save|log|remind|send|email|text|book|schedule|reply|respond)\b",
     "NAME+ACTION"),
    # "please file X, Lex" — imperative with name after
    (r"\b(file|add|create|capture|note|record|save|log|remind|send)\b[^.!?]{0,30}\bplease[, ]*\s*(Lex|Alex|Lexi|Alexa)\b",
     "ACTION_PLEASE_NAME"),
    # "file X, Lex" — action then name without "please" bridge
    (r"\b(file|add|create|capture|note|record|save|log|remind|send)\b[^.!?]{0,50}\b(Lex|Alex|Lexi|Alexa)\b",
     "ACTION_NAME"),
    # "Hey Lex, please..." or "OK Lex, do X"
    (r"\b(hey|ok|okay)\s+(Lex|Alex|Lexi|Alexa)\b[^.!?]{0,30}\b(please|file|add|create|capture|go ahead|send|note)\b",
     "HEY_NAME_ACTION"),
    # "Lex: yes, file it" or "Lex, do it, file that"
    (r"\b(Lex|Alex)\s*[,;:]\s*[^.!?]{0,20}\b(go ahead|yes|do it|file it|capture that|note that|remind me)\b",
     "NAME_AFFIRM_ACTION"),
]

_COMPILED: list[tuple[re.Pattern, str, str]] = []


def _compile_patterns() -> list[tuple[re.Pattern, str, str]]:
    if _COMPILED:
        return _COMPILED
    for pat, label in _SUMMONS_PATTERNS:
        _COMPILED.append((re.compile(pat, re.IGNORECASE | re.DOTALL), pat, label))
    return _COMPILED


def is_summons(text: str) -> bool:
    """Return True if *text* matches any summons / wake-word pattern.

    Typical input is a single caption line or the last N lines joined.
    """
    if not text or not text.strip():
        return False
    for compiled, _pat, _label in _compile_patterns():
        if compiled.search(text):
            return True
    return False


def match_summons(text: str) -> list[tuple[str, str]]:
    """Return all matching (pattern_label, match_text) tuples.

    Useful for debugging why a caption was flagged as a summons.
    """
    if not text or not text.strip():
        return []
    matches: list[tuple[str, str]] = []
    for compiled, _pat, label in _compile_patterns():
        m = compiled.search(text)
        if m:
            matches.append((label, m.group(0)[:120]))
    return matches


def is_summons_batch(lines: Iterable[str]) -> list[tuple[int, str, list[tuple[str, str]]]]:
    """Scan multiple lines and return (line_index, line, matches) for each summons.

    Batch version avoids one-call-per-line overhead in transcript scanning.
    """
    results: list[tuple[int, str, list[tuple[str, str]]]] = []
    for idx, line in enumerate(lines):
        ms = match_summons(line)
        if ms:
            results.append((idx, line, ms))
    return results
