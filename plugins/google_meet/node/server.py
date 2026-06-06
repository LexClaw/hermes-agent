"""Remote node server.

Runs on the machine that will host the Meet bot (typically the user's
Mac laptop with a signed-in Chrome). Exposes a WebSocket endpoint that
accepts signed RPC requests and dispatches them to the existing
``plugins.google_meet.process_manager`` module.

Launched by ``hermes meet node run``.

Token handling
--------------
On first boot we mint 32 hex chars of entropy and persist them at
``$HERMES_HOME/workspace/meetings/node_token.json``. Subsequent boots
reuse the same token so previously-approved gateways don't need to be
re-paired. The operator copies this token out-of-band to the gateway
via ``hermes meet node approve <name> <url> <token>``.

Dependencies
------------
``websockets`` is an optional dep. We import it lazily inside
:meth:`serve` so installing the plugin doesn't require it unless you
actually host a node.
"""

from __future__ import annotations

import json
import os
import platform
import secrets
import time
from pathlib import Path
from typing import Any, Dict, Optional

from hermes_constants import get_hermes_home
from plugins.google_meet.node import protocol as _proto


def _default_token_path() -> Path:
    return Path(get_hermes_home()) / "workspace" / "meetings" / "node_token.json"


class NodeServer:
    """WebSocket server that executes meet bot RPCs locally."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 18789,
        token_path: Optional[Path] = None,
        display_name: str = "hermes-meet-node",
    ) -> None:
        self.host = host
        self.port = port
        self.display_name = display_name
        self.token_path = Path(token_path) if token_path is not None else _default_token_path()
        self._token: Optional[str] = None

    # ----- token management --------------------------------------------

    def _default_chrome_profile(self) -> tuple[Optional[str], Optional[str]]:
        """Return (Chrome user-data root, profile name) for this node, if known."""
        if platform.system() != "Darwin":
            return None, None
        root = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
        if not root.is_dir():
            return None, None
        local_state = root / "Local State"
        if not local_state.is_file():
            return None, None
        try:
            data = json.loads(local_state.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            return None, None

        # Prefer lex@hitnetwork.io when present because the Meet bot identity is Lex.
        profiles = data.get("profile", {}).get("info_cache", {})
        target_name = None
        for name, info in profiles.items():
            if str(info.get("user_name") or "").lower() == "lex@hitnetwork.io":
                target_name = name
                break
        if target_name is None and (root / "Default").is_dir():
            target_name = "Default"
        if target_name is None:
            return None, None

        # Chrome locks the full user-data root while the human browser is open.
        # Copy just the selected profile plus Local State into a node-owned root
        # so Playwright can launch real Chrome without forcing TJ to quit Chrome.
        cache_root = Path(get_hermes_home()) / "workspace" / "meetings" / "chrome-node-profile"
        cache_root.mkdir(parents=True, exist_ok=True)
        (cache_root / "Local State").write_text(local_state.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        src = root / target_name
        dst = cache_root / target_name
        try:
            import shutil
            shutil.copytree(
                src,
                dst,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("Singleton*", "*.lock", "Crashpad", "Code Cache", "GPUCache"),
            )
        except OSError:
            return None, None
        return str(cache_root), target_name

    def ensure_token(self) -> str:
        """Return the persisted shared secret, generating one on first use."""
        if self._token:
            return self._token
        if self.token_path.is_file():
            try:
                data = json.loads(self.token_path.read_text(encoding="utf-8"))
                tok = data.get("token")
                if isinstance(tok, str) and tok:
                    self._token = tok
                    return tok
            except (OSError, json.JSONDecodeError):
                pass
        tok = secrets.token_hex(16)  # 32 hex chars
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.token_path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps({"token": tok, "generated_at": time.time()}, indent=2),
            encoding="utf-8",
        )
        # Restrict to owner-read-write only — the token grants full RPC
        # access to the meet bot (start, transcribe, speak in meetings).
        try:
            tmp.chmod(0o600)
        except (OSError, NotImplementedError):
            # Best-effort on non-POSIX filesystems; mode is set on POSIX.
            pass
        tmp.replace(self.token_path)
        self._token = tok
        return tok

    def get_token(self) -> str:
        """Alias for :meth:`ensure_token`; does not mutate on subsequent calls."""
        return self.ensure_token()

    # ----- dispatch -----------------------------------------------------

    async def _handle_request(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Validate + dispatch a single decoded request envelope.

        Always returns a response envelope (success or error); never
        raises. Errors from inside the process_manager are wrapped into
        the response payload's ``ok``/``error`` keys (which pm already
        does) rather than being re-encoded as error envelopes — the
        envelope-level error channel is reserved for auth / protocol
        failures.
        """
        expected = self.ensure_token()
        ok, reason = _proto.validate_request(msg, expected)
        if not ok:
            return _proto.make_error(str(msg.get("id") or ""), reason)

        req_id = msg["id"]
        t = msg["type"]
        payload = msg["payload"]

        # Import lazily so test mocks can monkeypatch freely.
        from plugins.google_meet import process_manager as pm

        try:
            if t == "ping":
                return {"type": "pong", "id": req_id,
                        "payload": {"display_name": self.display_name,
                                    "ts": time.time()}}
            if t == "start_bot":
                # Whitelist kwargs we pass through to pm.start.
                kwargs = {
                    k: payload[k]
                    for k in ("url", "guest_name", "duration", "headed",
                              "auth_state", "session_id", "out_dir", "mode")
                    if k in payload
                }
                if "url" not in kwargs:
                    return _proto.make_error(req_id, "missing 'url' in payload")
                payload_profile = payload.get("chrome_profile_dir")
                if payload_profile:
                    profile_dir, profile_name = str(payload_profile), payload.get("chrome_profile_name")
                else:
                    profile_dir, profile_name = self._default_chrome_profile()
                old_profile = os.environ.get("HERMES_MEET_CHROME_PROFILE_DIR")
                old_profile_name = os.environ.get("HERMES_MEET_CHROME_PROFILE_NAME")
                if profile_dir:
                    os.environ["HERMES_MEET_CHROME_PROFILE_DIR"] = str(profile_dir)
                    if profile_name:
                        os.environ["HERMES_MEET_CHROME_PROFILE_NAME"] = str(profile_name)
                try:
                    result = pm.start(**kwargs)
                finally:
                    if old_profile is None:
                        os.environ.pop("HERMES_MEET_CHROME_PROFILE_DIR", None)
                    else:
                        os.environ["HERMES_MEET_CHROME_PROFILE_DIR"] = old_profile
                    if old_profile_name is None:
                        os.environ.pop("HERMES_MEET_CHROME_PROFILE_NAME", None)
                    else:
                        os.environ["HERMES_MEET_CHROME_PROFILE_NAME"] = old_profile_name
                return _proto.make_response(req_id, result)
            if t == "stop":
                reason_arg = payload.get("reason", "requested")
                result = pm.stop(reason=reason_arg)
                return _proto.make_response(req_id, result)
            if t == "status":
                return _proto.make_response(req_id, pm.status())
            if t == "transcript":
                last = payload.get("last")
                result = pm.transcript(last=last)
                return _proto.make_response(req_id, result)
            if t == "say":
                # v2 wiring: enqueue into say_queue.jsonl inside the
                # active meeting's out_dir when present. The bot-side
                # consumer is v3+ (for v1 this is a stub returning ok).
                text = payload.get("text", "")
                active = pm._read_active()  # type: ignore[attr-defined]
                enqueued = False
                if active and active.get("out_dir"):
                    queue = Path(active["out_dir"]) / "say_queue.jsonl"
                    try:
                        queue.parent.mkdir(parents=True, exist_ok=True)
                        with queue.open("a", encoding="utf-8") as fh:
                            fh.write(json.dumps({"text": text, "ts": time.time()}) + "\n")
                        enqueued = True
                    except OSError:
                        enqueued = False
                return _proto.make_response(
                    req_id,
                    {"ok": True, "enqueued": enqueued, "text": text},
                )
        except Exception as exc:  # noqa: BLE001 — surface any pm crash to client
            return _proto.make_error(req_id, f"{type(exc).__name__}: {exc}")

        return _proto.make_error(req_id, f"unhandled type: {t!r}")

    # ----- server loop --------------------------------------------------

    async def serve(self) -> None:
        """Run the WebSocket server until cancelled.

        Blocks forever. Callers typically wrap this in ``asyncio.run``.
        """
        try:
            import websockets  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "NodeServer.serve requires the 'websockets' package. "
                "Install it with: pip install websockets"
            ) from exc

        self.ensure_token()

        async def _handler(ws):
            async for raw in ws:
                try:
                    msg = _proto.decode(raw if isinstance(raw, str) else raw.decode("utf-8"))
                except ValueError as exc:
                    await ws.send(_proto.encode(_proto.make_error("", f"decode: {exc}")))
                    continue
                reply = await self._handle_request(msg)
                await ws.send(_proto.encode(reply))

        async with websockets.serve(_handler, self.host, self.port):
            # Run until cancelled.
            import asyncio
            await asyncio.Future()
