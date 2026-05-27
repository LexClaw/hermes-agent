"""Cartesia HTTP TTS client + drop-in replacement for :class:`RealtimeSession`.

This module replaces the OpenAI Realtime synth path for the Meet bot.
Architecture: text -> Cartesia /tts/bytes (streaming) -> PCM16 24kHz mono
-> (a) appended to ``audio_sink_path`` (for paplay tail-read on Linux) AND
(b) optional ``on_audio`` callback for in-process pumps (sounddevice on
macOS).

The streaming pattern mirrors the voice-server pattern in
``~/.hermes/voice-server/cartesia-tts.mjs`` (sentence buffer not needed
here because Meet bot's ``meet_say`` passes the full utterance up front).

Public surface matches the subset of :class:`RealtimeSession` that
:class:`RealtimeSpeaker` and ``meet_bot`` actually use: ``connect``,
``speak``, ``cancel_response``, ``close``, plus ``audio_bytes_out`` /
``last_audio_out_at`` counters.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any, Callable, Optional


CARTESIA_URL = "https://api.cartesia.ai/tts/bytes"
CARTESIA_VERSION = "2024-06-10"
DEFAULT_MODEL_ID = "sonic-2"


class CartesiaSession:
    """Thin Cartesia REST streaming client matching RealtimeSession's API.

    Usage::

        sess = CartesiaSession(api_key=..., voice_id=..., audio_sink_path=...)
        sess.connect()              # no-op, present for symmetry
        sess.speak("Hello team.")
        sess.close()
    """

    def __init__(
        self,
        api_key: str,
        voice_id: str,
        model_id: str = DEFAULT_MODEL_ID,
        audio_sink_path: Optional[Path] = None,
        sample_rate: int = 24000,
        on_audio: Optional[Callable[[bytes], None]] = None,
    ) -> None:
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.audio_sink_path = Path(audio_sink_path) if audio_sink_path else None
        self.sample_rate = sample_rate
        self.on_audio = on_audio
        self.audio_bytes_out: int = 0
        self.last_audio_out_at: Optional[float] = None
        self._cancel_flag = threading.Event()
        self._lock = threading.Lock()

    # symmetry with RealtimeSession ---------------------------------------

    def connect(self) -> None:
        # Cartesia is HTTP; no persistent connection.
        if not self.api_key or not self.voice_id:
            raise RuntimeError(
                "CartesiaSession: api_key and voice_id are required"
            )

    def close(self) -> None:
        # No socket to close. Reset cancel so a re-used instance behaves.
        self._cancel_flag.clear()

    def cancel_response(self) -> bool:
        """Abort the currently-streaming Cartesia response. Barge-in hook."""
        self._cancel_flag.set()
        return True

    # core ----------------------------------------------------------------

    def speak(self, text: str, timeout: float = 30.0) -> dict:
        """POST text to Cartesia, stream PCM back, append to sink + callback."""
        text = (text or "").strip()
        if not text:
            return {"ok": True, "bytes_written": 0, "duration_ms": 0.0}

        try:
            import requests  # local import: optional dep gate
        except ImportError as exc:
            raise RuntimeError(
                "requests package required for Cartesia synth path"
            ) from exc

        # Serialize cancel resets so concurrent speak() calls don't race
        # (RealtimeSpeaker is single-threaded today, defense-in-depth).
        with self._lock:
            self._cancel_flag.clear()

        body = {
            "model_id": self.model_id,
            "transcript": text,
            "voice": {"mode": "id", "id": self.voice_id},
            "output_format": {
                "container": "raw",
                "encoding": "pcm_s16le",
                "sample_rate": self.sample_rate,
            },
            "language": "en",
        }
        headers = {
            "Cartesia-Version": CARTESIA_VERSION,
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

        start = time.monotonic()
        bytes_written = 0
        sink_fp = None
        if self.audio_sink_path is not None:
            self.audio_sink_path.parent.mkdir(parents=True, exist_ok=True)
            sink_fp = open(self.audio_sink_path, "ab")

        try:
            with requests.post(
                CARTESIA_URL,
                json=body,
                headers=headers,
                stream=True,
                timeout=timeout,
            ) as resp:
                if resp.status_code != 200:
                    err = resp.text[:300] if resp.text else f"http {resp.status_code}"
                    raise RuntimeError(f"cartesia {resp.status_code}: {err}")

                for chunk in resp.iter_content(chunk_size=4096):
                    if self._cancel_flag.is_set():
                        break
                    if not chunk:
                        continue
                    if sink_fp is not None:
                        sink_fp.write(chunk)
                        sink_fp.flush()
                    if self.on_audio is not None:
                        try:
                            self.on_audio(chunk)
                        except Exception:
                            # Pump failures must not kill the synth call.
                            pass
                    bytes_written += len(chunk)
                    self.audio_bytes_out += len(chunk)
                    self.last_audio_out_at = time.time()
        finally:
            if sink_fp is not None:
                sink_fp.close()

        duration_ms = (time.monotonic() - start) * 1000.0
        return {
            "ok": True,
            "bytes_written": bytes_written,
            "duration_ms": duration_ms,
            "cancelled": self._cancel_flag.is_set(),
        }
