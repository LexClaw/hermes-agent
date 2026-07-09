"""Per-agent model fallback policy and telemetry helpers."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from hermes_constants import get_default_hermes_root, get_hermes_home


TIER_RS_AGENTS = {"grant", "reid", "will", "ed", "cal", "sage", "nora"}
TIER_RS_MODELS = (
    "claude-opus",
    "claude-sonnet",
    "gpt-5",
)
CHEAP_QWEN_MARKERS = (
    "qwen",
    "qwen3",
    "qwen-",
)


def active_profile_name() -> str:
    home = get_hermes_home().expanduser().resolve()
    if home.parent.name == "profiles":
        return home.name.lower()
    return os.environ.get("HERMES_AGENT_PROFILE", "").strip().lower() or "default"


def _workspace_model_config_path() -> Path:
    return get_default_hermes_root() / "workspace" / "config" / "model-config.json"


def load_workspace_model_config(path: Optional[Path] = None) -> Dict[str, Any]:
    cfg_path = path or _workspace_model_config_path()
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _fallback_entries_from_policy(policy: Dict[str, Any]) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    raw_chain = policy.get("fallback_providers") or policy.get("fallback_chain")
    if isinstance(raw_chain, list):
        for item in raw_chain:
            if isinstance(item, dict) and item.get("provider") and item.get("model"):
                entries.append({k: str(v) for k, v in item.items() if v is not None})
    fb = policy.get("fallback")
    if isinstance(fb, dict) and fb.get("provider") and fb.get("model"):
        entries.append({k: str(v) for k, v in fb.items() if v is not None})
    if policy.get("fallback_provider") and policy.get("fallback_model"):
        entries.append({
            "provider": str(policy["fallback_provider"]),
            "model": str(policy["fallback_model"]),
        })
    seen = set()
    unique: List[Dict[str, str]] = []
    for item in entries:
        key = (item.get("provider", "").lower(), item.get("model", ""))
        if key not in seen:
            unique.append(item)
            seen.add(key)
    return unique


def _is_tier_rs(agent_name: str, provider: str, model: str) -> bool:
    if agent_name in TIER_RS_AGENTS:
        return True
    text = f"{provider}/{model}".lower()
    return any(marker in text for marker in TIER_RS_MODELS)


def _tier_rs_default_chain(provider: str, model: str, config: Dict[str, Any]) -> List[Dict[str, str]]:
    raw_strong = config.get("fallback_strong")
    strong: Dict[str, Any] = raw_strong if isinstance(raw_strong, dict) else {}
    strong_provider = str(strong.get("provider") or "openrouter")
    strong_model = str(strong.get("model") or "openai/gpt-5.5")
    chain = [
        {"provider": "anthropic", "model": "claude-sonnet-4-6"},
        {"provider": strong_provider, "model": strong_model},
    ]
    current = (provider.lower(), model)
    return [item for item in chain if (item["provider"].lower(), item["model"]) != current]


def resolve_per_agent_fallback_chain(
    *,
    provider: str,
    model: str,
    explicit_fallback: Any = None,
    agent_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    """Return the runtime fallback chain for this agent/profile.

    Workspace model-config is authoritative for named profiles. Explicit runtime
    fallback remains the default for unnamed low-tier sessions.
    """
    cfg = config if config is not None else load_workspace_model_config()
    name = (agent_name or active_profile_name()).strip().lower()
    raw_policy = cfg.get(name)
    policy: Dict[str, Any] = raw_policy if isinstance(raw_policy, dict) else {}
    policy_chain = _fallback_entries_from_policy(policy)
    if policy_chain:
        return policy_chain
    if _is_tier_rs(name, provider, model):
        return _tier_rs_default_chain(provider, model, cfg)
    if isinstance(explicit_fallback, list):
        return [
            {k: str(v) for k, v in item.items() if v is not None}
            for item in explicit_fallback
            if isinstance(item, dict) and item.get("provider") and item.get("model")
        ]
    if isinstance(explicit_fallback, dict) and explicit_fallback.get("provider") and explicit_fallback.get("model"):
        return [{k: str(v) for k, v in explicit_fallback.items() if v is not None}]
    return []


def infer_job_id(session_id: str) -> str:
    if not session_id.startswith("cron_"):
        return ""
    rest = session_id[len("cron_"):]
    if "_" not in rest:
        return ""
    return rest.rsplit("_", 1)[0]


def telemetry_event(agent: Any, *, from_provider: str, from_model: str, to_provider: str, to_model: str, reason: Any = None, exception: str = "") -> Dict[str, Any]:
    session_id = str(getattr(agent, "session_id", "") or "")
    source = str(getattr(agent, "platform", "") or os.environ.get("HERMES_SESSION_SOURCE", "") or "unknown")
    now = datetime.now(timezone.utc)
    return {
        "timestamp": now.isoformat(),
        "timestamp_unix": now.timestamp(),
        "session_id": session_id,
        "job_id": infer_job_id(session_id),
        "source": source,
        "agent_profile": active_profile_name(),
        "from_provider": from_provider,
        "from_model": from_model,
        "to_provider": to_provider,
        "to_model": to_model,
        "reason": getattr(reason, "value", str(reason or "unknown")),
        "exception": exception,
    }


def _telemetry_jsonl_path() -> Path:
    return get_default_hermes_root() / "workspace" / "logs" / "model-fallback-telemetry.jsonl"


def record_fallback_event(agent: Any, event: Dict[str, Any]) -> None:
    path = _telemetry_jsonl_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")
    except Exception:
        pass
    db = getattr(agent, "_session_db", None)
    if db is None:
        return
    try:
        if hasattr(db, "record_model_fallback_event"):
            db.record_model_fallback_event(event)
    except Exception:
        pass


def is_cheap_qwen(provider: str, model: str) -> bool:
    text = f"{provider}/{model}".lower()
    return any(marker in text for marker in CHEAP_QWEN_MARKERS)


def summarize_recent_fallbacks(events: Iterable[Dict[str, Any]], *, now: Optional[float] = None, hours: int = 24) -> Dict[str, Any]:
    now_ts = time.time() if now is None else now
    cutoff = now_ts - hours * 3600
    recent = []
    tier_rs = []
    for event in events:
        ts = event.get("timestamp_unix")
        if ts is None:
            try:
                ts = datetime.fromisoformat(str(event.get("timestamp", "")).replace("Z", "+00:00")).timestamp()
            except Exception:
                continue
        if float(ts) < cutoff:
            continue
        recent.append(event)
        agent_name = str(event.get("agent_profile") or "").lower()
        from_model = str(event.get("from_model") or "")
        from_provider = str(event.get("from_provider") or "")
        if _is_tier_rs(agent_name, from_provider, from_model):
            tier_rs.append(event)
    return {"total": len(recent), "tier_rs": len(tier_rs), "events": recent, "tier_rs_events": tier_rs}
