from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_per_agent_fallback_policy_uses_workspace_config(monkeypatch, tmp_path):
    home = tmp_path / ".hermes" / "profiles" / "will"
    cfg_dir = tmp_path / ".hermes" / "workspace" / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "model-config.json").write_text(json.dumps({
        "will": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-6",
            "fallback_provider": "anthropic",
            "fallback_model": "claude-opus-4-8",
        },
        "fallback_strong": {"provider": "openrouter", "model": "openai/gpt-5.5"},
    }))
    monkeypatch.setenv("HERMES_HOME", str(home))

    from agent.model_fallback_policy import resolve_per_agent_fallback_chain

    chain = resolve_per_agent_fallback_chain(
        provider="anthropic",
        model="claude-sonnet-4-6",
        explicit_fallback={"provider": "openrouter", "model": "qwen/qwen3.6-plus"},
    )

    assert chain == [{"provider": "anthropic", "model": "claude-opus-4-8"}]


def test_tier_rs_default_fallback_fails_loud_without_canonical_route(monkeypatch, tmp_path):
    home = tmp_path / ".hermes" / "profiles" / "grant"
    cfg_dir = tmp_path / ".hermes" / "workspace" / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "model-config.json").write_text(json.dumps({
        "grant": {"provider": "anthropic", "model": "claude-opus-4-8"},
        "fallback_strong": {"provider": "openrouter", "model": "openai/gpt-5.5"},
    }))
    monkeypatch.setenv("HERMES_HOME", str(home))

    from agent.model_fallback_policy import resolve_per_agent_fallback_chain, is_cheap_qwen

    chain = resolve_per_agent_fallback_chain(
        provider="anthropic",
        model="claude-opus-4-8",
        explicit_fallback={"provider": "openrouter", "model": "qwen/qwen3.6-plus"},
    )

    assert chain == []


def test_forced_fallback_records_jsonl_and_state_db(monkeypatch, tmp_path):
    home = tmp_path / ".hermes"
    monkeypatch.setenv("HERMES_HOME", str(home))

    from hermes_state import SessionDB
    from agent.chat_completion_helpers import try_activate_fallback
    import agent.auxiliary_client as auxiliary_client
    import agent.chat_completion_helpers as helpers

    db = SessionDB(home / "state.db")
    db.create_session("sess1", "cli", model="claude-opus-4-8")

    def fake_resolve(provider, model, raw_codex=False, explicit_base_url=None, explicit_api_key=None):
        return SimpleNamespace(api_key="test-key", base_url="https://example.test/v1"), model

    monkeypatch.setattr(auxiliary_client, "resolve_provider_client", fake_resolve)
    monkeypatch.setattr(helpers, "get_provider_request_timeout", lambda provider, model: None)

    class DummyAgent:
        def __init__(self):
            self._fallback_index = 0
            self._fallback_chain = [{"provider": "openrouter", "model": "openai/gpt-5.5"}]
            self.provider = "anthropic"
            self.model = "claude-opus-4-8"
            self.base_url = "https://api.anthropic.com"
            self.api_mode = "anthropic_messages"
            self._fallback_activated = False
            self._primary_runtime = {"provider": "anthropic"}
            self._rate_limited_until = 0
            self._transport_cache = {}
            self._credential_pool = None
            self._config_context_length = None
            self.context_compressor = None
            self._cached_system_prompt = "Model: claude-opus-4-8\nProvider: anthropic"
            self._session_db = db
            self.session_id = "sess1"
            self.platform = "cli"

        def _try_activate_fallback(self):
            return try_activate_fallback(self)

        def _is_azure_openai_url(self, base_url=None):
            return False

        def _is_direct_openai_url(self, base_url=None):
            return False

        def _provider_model_requires_responses_api(self, model, provider=None):
            return False

        def _anthropic_prompt_cache_policy(self, provider=None, base_url=None, api_mode=None, model=None):
            return False, False

        def _ensure_lmstudio_runtime_loaded(self):
            return None

        def _buffer_status(self, text):
            self.status = text

    agent = DummyAgent()

    assert try_activate_fallback(agent) is True
    assert agent.provider == "openrouter"
    assert agent.model == "openai/gpt-5.5"

    log_path = home / "workspace" / "logs" / "model-fallback-telemetry.jsonl"
    rows = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert rows[-1]["session_id"] == "sess1"
    assert rows[-1]["from_provider"] == "anthropic"
    assert rows[-1]["to_provider"] == "openrouter"

    db_rows = db.list_model_fallback_events()
    assert db_rows[0]["session_id"] == "sess1"
    assert db_rows[0]["to_model"] == "openai/gpt-5.5"


def test_grant_verdict_lane_uses_its_canonical_codex_fallback(monkeypatch, tmp_path):
    home = tmp_path / ".hermes" / "profiles" / "grant"
    cfg_dir = tmp_path / ".hermes" / "workspace" / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "model-config.json").write_text(json.dumps({
        "grant": {
            "provider": "openai-codex",
            "model": "gpt-5.6-terra",
            "fallback_provider": "openai-codex",
            "fallback_model": "gpt-5.6-terra",
        },
    }))
    monkeypatch.setenv("HERMES_HOME", str(home))

    from agent.model_fallback_policy import resolve_per_agent_fallback_chain, is_cheap_qwen

    chain = resolve_per_agent_fallback_chain(
        provider="openai-codex",
        model="gpt-5.6-sol",
        explicit_fallback={"provider": "openrouter", "model": "qwen/qwen3.6-plus"},
    )

    assert chain == [{"provider": "openai-codex", "model": "gpt-5.6-terra"}]
    assert not any(is_cheap_qwen(item["provider"], item["model"]) for item in chain)


def test_unnamed_tier_rs_runtime_fails_loud_without_canonical_policy(monkeypatch, tmp_path):
    home = tmp_path / ".hermes"
    cfg_dir = home / "workspace" / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "model-config.json").write_text("{}")
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.delenv("HERMES_AGENT_PROFILE", raising=False)

    from agent.model_fallback_policy import resolve_per_agent_fallback_chain

    chain = resolve_per_agent_fallback_chain(
        provider="anthropic",
        model="claude-opus-4-8",
        explicit_fallback={"provider": "openrouter", "model": "qwen/qwen3.6-plus"},
    )

    assert chain == []
