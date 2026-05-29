#!/usr/bin/env python3
"""Local Hit Network ALE skill telemetry adapter.

Optional local integration for annotating the active ALE run with skills loaded
through skill_view().  It is disabled unless the live switch file is enabled and
all failures are fail-open.
"""
from __future__ import annotations

import contextvars
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Optional

current_ale_run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_ale_run_id", default=None
)

_DEFAULT_DB_PATH = Path.home() / ".hermes" / "workspace" / "agents" / "ale" / "ale.db"
_SWITCH_PATH = Path.home() / ".hermes" / "workspace" / "config" / "ale-skill-telemetry.enabled"
_ALE_CLI_PATH = Path.home() / "hermes-workspace" / "Lex-Workspace" / "agents" / "ale" / "cli.py"
_ENABLED_VALUES = {"1", "true", "enabled"}


def telemetry_enabled() -> bool:
    """Read the live kill switch on every telemetry attempt."""
    try:
        return _SWITCH_PATH.read_text(encoding="utf-8").strip().lower() in _ENABLED_VALUES
    except OSError:
        return False


def get_db_path() -> Path:
    override = os.environ.get("HERMES_ALE_DB_PATH")
    if override:
        return Path(override).expanduser()
    return _DEFAULT_DB_PATH


def set_current_run_id(run_id: str | None):
    return current_ale_run_id.set(run_id or None)


def reset_current_run_id(token) -> None:
    current_ale_run_id.reset(token)


def get_current_run_id(explicit: str | None = None) -> str | None:
    if explicit:
        return explicit
    env_run_id = os.environ.get("HERMES_ALE_RUN_ID")
    if env_run_id:
        return env_run_id
    return current_ale_run_id.get()


def _canonical_skill_name(skill_name: str) -> str:
    return (skill_name or "").strip()


def record_skill_load(skill_name: str, run_id: str | None = None) -> None:
    """Append skill_name once to runs.skill_code for the active ALE run.

    Intentionally returns None for every failure mode: disabled switch, missing
    run id, missing DB, locked DB, missing row, malformed CSV, and unexpected
    exceptions are all non-fatal to skill_view().
    """
    if not telemetry_enabled():
        return
    skill = _canonical_skill_name(skill_name)
    if not skill:
        return
    active_run_id = get_current_run_id(run_id)
    if not active_run_id:
        return
    db_path = get_db_path()
    if not db_path.exists():
        return

    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(db_path), timeout=0.025)
        conn.execute("PRAGMA busy_timeout=25")
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT skill_code FROM runs WHERE run_id=?", (active_run_id,)
        ).fetchone()
        if row is None:
            conn.commit()
            return
        existing = row[0] or ""
        skills = [part.strip() for part in str(existing).split(",") if part.strip()]
        if skill in skills:
            conn.commit()
            return
        skills.append(skill)
        conn.execute(
            "UPDATE runs SET skill_code=? WHERE run_id=?",
            (",".join(skills), active_run_id),
        )
        conn.commit()
    except BaseException as exc:  # fail-open, but preserve process interrupts
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        try:
            if conn is not None:
                conn.rollback()
        except Exception:
            pass
        return
    finally:
        try:
            if conn is not None:
                conn.close()
        except Exception:
            pass


def start_gateway_run(*, model: str, summary: str) -> str | None:
    """Start a turn-scoped Lex ALE run. Disabled or failures return None."""
    if not telemetry_enabled():
        return None
    if not _ALE_CLI_PATH.exists():
        return None
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(_ALE_CLI_PATH),
                "start-run",
                "--agent",
                "lex",
                "--model",
                model or "unknown",
                "--task-type",
                "gateway-turn",
                "--summary",
                summary[:200],
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode != 0:
            return None
        run_id = result.stdout.strip().splitlines()[-1].strip()
        return run_id or None
    except Exception:
        return None


def end_gateway_run(run_id: str | None, *, status: str) -> None:
    if not run_id or not telemetry_enabled() or not _ALE_CLI_PATH.exists():
        return
    try:
        subprocess.run(
            [
                sys.executable,
                str(_ALE_CLI_PATH),
                "end-run",
                "--run-id",
                run_id,
                "--status",
                status or "success",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
    except Exception:
        return
