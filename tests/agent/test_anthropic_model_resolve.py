"""Tests for Anthropic model ID normalization and fail-loud behavior.

Regression tests for silent-Sonnet-fallback bug (MC card
kn7b995np6yzda83ersspkk49x8807fm).  When a malformed model id
(e.g. ``anthropic/claude-opus-4.8`` with dots and prefix) is handed to
the direct Anthropic provider, it must be normalized to a registered
bare id.  If normalization still cannot resolve to a registered id, the
code must raise a clear error instead of silently falling back to the
registry default (claude-sonnet-4-20250514).
"""

import pytest

from agent.anthropic_adapter import (
    normalize_model_name,
    resolve_anthropic_model_id,
    _is_bedrock_model_id,
)
from hermes_cli.model_normalize import normalize_model_for_provider


# ── normalize_model_name ─────────────────────────────────────────────

class TestNormalizeModelName:
    """verify that OpenRouter-style prefixes and dot versions are stripped."""

    def test_strips_anthropic_prefix(self):
        """anthropic/claude-opus-4.8 → claude-opus-4-8 (prefix stripped, dots converted)."""
        assert normalize_model_name("anthropic/claude-opus-4.8") == "claude-opus-4-8"

    def test_strips_prefix_case_insensitive(self):
        """ANTHROPIC/... and Anthropic/... are both stripped."""
        assert normalize_model_name("Anthropic/claude-opus-4.6") == "claude-opus-4-6"
        assert normalize_model_name("ANTHROPIC/claude-opus-4.6") == "claude-opus-4-6"

    def test_dots_to_hyphens(self):
        """claude-opus-4.8 → claude-opus-4-8."""
        assert normalize_model_name("claude-opus-4.8") == "claude-opus-4-8"

    def test_combined_prefix_and_dot(self):
        """anthropic/claude-opus-4.8 → claude-opus-4-8 (both transforms)."""
        assert normalize_model_name("anthropic/claude-opus-4.8") == "claude-opus-4-8"

    def test_bare_registered_id_unchanged(self):
        """Already-correct bare id passes through untouched."""
        assert normalize_model_name("claude-opus-4-8") == "claude-opus-4-8"
        assert normalize_model_name("claude-sonnet-4-6") == "claude-sonnet-4-6"

    def test_preserves_dots_when_flagged(self):
        """preserve_dots=True suppresses dot-to-hyphen conversion."""
        result = normalize_model_name("claude-opus-4.8", preserve_dots=True)
        assert result == "claude-opus-4.8"

    def test_bedrock_ids_preserved(self):
        """Bedrock dot-style ids are not mangled."""
        assert normalize_model_name("anthropic.claude-opus-4-7") == "anthropic.claude-opus-4-7"
        assert normalize_model_name("us.anthropic.claude-opus-4-7") == "us.anthropic.claude-opus-4-7"


# ── resolve_anthropic_model_id ───────────────────────────────────────

class TestResolveAnthropicModelId:
    """verify that normalized model ids resolve, and unknown ids fail loud."""

    def test_normalize_success_prefix_and_dot(self):
        """anthropic/claude-opus-4.8 normalizes and resolves to registered id."""
        resolved = resolve_anthropic_model_id("anthropic/claude-opus-4.8")
        assert resolved == "claude-opus-4-8"

    def test_normalize_success_bare_with_dot(self):
        """claude-sonnet-4.5 normalizes dot to hyphen and resolves."""
        resolved = resolve_anthropic_model_id("claude-sonnet-4.5")
        assert resolved == "claude-sonnet-4-5"

    def test_bare_registered_id_passthrough(self):
        """Already-correct id returns unchanged."""
        resolved = resolve_anthropic_model_id("claude-opus-4-6")
        assert resolved == "claude-opus-4-6"

    def test_fails_loud_on_unknown_model(self):
        """A genuinely unregistered model id raises ValueError with details."""
        with pytest.raises(ValueError) as exc_info:
            resolve_anthropic_model_id("claude-nonexistent-9")
        err = str(exc_info.value)
        # Error must name the unresolvable id
        assert "claude-nonexistent-9" in err
        # Error must name the provider
        assert "anthropic" in err.lower()
        # Error must suggest registered ids exist
        assert "claude" in err.lower()

    def test_fails_loud_on_unknown_with_prefix(self):
        """Even after stripping an unknown prefixed id, fails loud."""
        with pytest.raises(ValueError) as exc_info:
            resolve_anthropic_model_id("anthropic/claude-fake-99")
        err = str(exc_info.value)
        assert "claude-fake-99" in err
        assert "anthropic" in err.lower()

    def test_registered_with_datestamp(self):
        """Date-stamped ids from the register resolve correctly."""
        resolved = resolve_anthropic_model_id("claude-opus-4-20250514")
        assert resolved == "claude-opus-4-20250514"


def test_normalize_model_for_provider_anthropic_validates_model_id():
    """Anthropic provider normalization uses the resolver, not silent fallback."""
    assert (
        normalize_model_for_provider("anthropic/claude-opus-4.8", "anthropic")
        == "claude-opus-4-8"
    )

    with pytest.raises(ValueError):
        normalize_model_for_provider("claude-bogus-9", "anthropic")
