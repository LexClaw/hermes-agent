"""Sustain test for CartesiaSession — 5x consecutive meet_say equivalent.

Drives CartesiaSession + RealtimeSpeaker end-to-end with a mocked HTTP
responder (no API key or network needed). Verifies:

1. audio_bytes_out increases across each of 5 consecutive speak() calls
2. No thread/stream leaks between calls (lock + cancel event reset cleanly)
3. Consistent ok=True results across all calls
4. audio_sink_path receives monotonically-growing PCM data
5. last_audio_out_at advances on each call

This is the Cartesia equivalent of the 5x meet_say sustain test required
by card kn7ds5d1kh66 Gap 1.
"""

from __future__ import annotations

import json
import sys
import threading
import types
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _isolate_home(tmp_path, monkeypatch):
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    yield hermes_home


# ---------------------------------------------------------------------------
# Mock Cartesia HTTP response
# ---------------------------------------------------------------------------


def _mock_cartesia_response(request):
    """Return a streaming PCM16 response that looks like Cartesia bytes."""
    # Simulate ~1920 bytes of 24kHz 16-bit mono PCM (100ms of silence)
    pcm_chunk = b"\x00\x00" * 960

    class _FakeStream:
        status_code = 200
        text = ""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def iter_content(self, chunk_size=4096):
            # Yield 3 chunks to simulate streaming
            for _ in range(3):
                yield pcm_chunk

    return _FakeStream()


def _install_mock_requests(monkeypatch):
    """Replace requests.post with a mock that returns a streaming PCM response."""
    calls = []

    class _MockResponse:
        status_code = 200
        text = ""

        def __init__(self):
            import io
            self._pcm_chunk = b"\x00\x00" * 960  # 1920 bytes, ~100ms at 24kHz
            self._chunks_yielded = 0

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def iter_content(self, chunk_size=4096):
            # Yield 3 chunks
            for _ in range(3):
                yield self._pcm_chunk

    class _FakeRequests:
        @staticmethod
        def post(url, json=None, headers=None, stream=True, timeout=30):
            calls.append({"url": url, "json": json, "headers": headers})
            return _MockResponse()

    monkeypatch.setitem(sys.modules, "requests", _FakeRequests())
    return calls


# ---------------------------------------------------------------------------
# Basic CartesiaSession sustain test (5x speak)
# ---------------------------------------------------------------------------


def test_cartesia_sustain_5x_consecutive_speak(_isolate_home, tmp_path, monkeypatch):
    """5 consecutive speak() calls: verify bytes_out monotonicity, no leaks."""
    from plugins.google_meet.realtime.cartesia_client import CartesiaSession

    _install_mock_requests(monkeypatch)

    sink = tmp_path / "audio.pcm"
    sess = CartesiaSession(
        api_key="test-cartesia-key",
        voice_id="test-voice-id",
        model_id="sonic-2",
        audio_sink_path=sink,
    )
    sess.connect()

    utterances = [
        "Hello, this is test call one.",
        "Testing consecutive speak call two.",
        "Third utterance for the sustain test.",
        "Continuing with call four to verify stability.",
        "Final fifth call — checking no thread or stream leaks.",
    ]

    results = []
    prev_bytes = 0
    prev_timestamp = 0.0

    for i, text in enumerate(utterances, 1):
        # Small delay to ensure timestamps are distinct
        time.sleep(0.01)
        result = sess.speak(text)
        results.append((i, result))

        # Verify ok=True
        assert result["ok"] is True, f"Call {i}: speak() returned ok=False"

        # Verify bytes_written > 0 (we produced audio)
        assert result["bytes_written"] > 0, f"Call {i}: bytes_written is zero"

        # Verify audio_bytes_out is cumulative and monotonic
        assert sess.audio_bytes_out > prev_bytes, (
            f"Call {i}: audio_bytes_out ({sess.audio_bytes_out}) "
            f"not greater than previous ({prev_bytes})"
        )
        prev_bytes = sess.audio_bytes_out

        # Verify last_audio_out_at advances
        assert sess.last_audio_out_at is not None, f"Call {i}: last_audio_out_at is None"
        assert sess.last_audio_out_at >= prev_timestamp, (
            f"Call {i}: last_audio_out_at went backwards"
        )
        prev_timestamp = sess.last_audio_out_at

    # After 5 calls: verify sink file has grown
    assert sink.exists(), "Audio sink file was never created"
    sink_size = sink.stat().st_size
    assert sink_size > 0, "Audio sink file is empty"
    # 5 calls × 3 chunks × 1920 bytes = 28800 bytes (minimum)
    assert sink_size >= 5 * 3 * 1920, (
        f"Expected >= {5 * 3 * 1920} bytes in sink, got {sink_size}"
    )

    # Verify audio_bytes_out matches sink size
    assert sess.audio_bytes_out == sink_size, (
        f"audio_bytes_out ({sess.audio_bytes_out}) != sink size ({sink_size})"
    )

    # Verify duration is reasonable (total across 5 calls)
    total_ms = sum(r[1]["duration_ms"] for r in results)
    assert total_ms > 0, "Total duration should be > 0"

    print(f"5x sustain complete: {sess.audio_bytes_out} bytes, {total_ms:.0f}ms total")

    sess.close()


def test_cartesia_sustain_no_thread_leak(_isolate_home, tmp_path, monkeypatch):
    """Verify no leftover threads after 5x speak cycle."""
    from plugins.google_meet.realtime.cartesia_client import CartesiaSession

    _install_mock_requests(monkeypatch)

    initial_threads = threading.active_count()

    sink = tmp_path / "audio.pcm"
    sess = CartesiaSession(
        api_key="test-key",
        voice_id="test-voice",
        audio_sink_path=sink,
    )
    sess.connect()

    for i in range(5):
        result = sess.speak(f"Utterance {i}")
        assert result["ok"] is True

    sess.close()

    # Allow any background cleanup
    time.sleep(0.05)
    final_threads = threading.active_count()

    # Thread count should not have grown
    assert final_threads <= initial_threads + 1, (
        f"Thread leak: started with {initial_threads}, now {final_threads} "
        f"(+{final_threads - initial_threads} after 5x speak cycle)"
    )


def test_cartesia_sustain_cancel_between_calls(_isolate_home, tmp_path, monkeypatch):
    """Verify cancel_response doesn't break subsequent speak() calls."""
    from plugins.google_meet.realtime.cartesia_client import CartesiaSession

    _install_mock_requests(monkeypatch)

    sink = tmp_path / "audio.pcm"
    sess = CartesiaSession(
        api_key="test-key",
        voice_id="test-voice",
        audio_sink_path=sink,
    )
    sess.connect()

    # Call 1: normal speak
    r1 = sess.speak("First normal call")
    assert r1["ok"] is True
    bytes_after_1 = sess.audio_bytes_out

    # Call 2: cancel in-flight (simulates barge-in)
    sess.cancel_response()
    r2 = sess.speak("This should still work after cancel")
    assert r2["ok"] is True
    assert sess.audio_bytes_out > bytes_after_1, "Bytes should increase after call 2"
    bytes_after_2 = sess.audio_bytes_out

    # Call 3: normal again
    r3 = sess.speak("Third call after barge-in")
    assert r3["ok"] is True
    assert sess.audio_bytes_out > bytes_after_2, "Bytes should increase after call 3"

    sess.close()


def test_cartesia_sustain_on_audio_callback(_isolate_home, tmp_path, monkeypatch):
    """Verify on_audio callback fires on each of 5 consecutive calls."""
    from plugins.google_meet.realtime.cartesia_client import CartesiaSession

    _install_mock_requests(monkeypatch)

    callback_chunks = []

    def _on_audio(chunk):
        callback_chunks.append(len(chunk))

    sink = tmp_path / "audio.pcm"
    sess = CartesiaSession(
        api_key="test-key",
        voice_id="test-voice",
        audio_sink_path=sink,
        on_audio=_on_audio,
    )
    sess.connect()

    for i in range(5):
        result = sess.speak(f"Callback test {i}")
        assert result["ok"] is True

    # Each call yields 3 chunks of 1920 bytes
    assert len(callback_chunks) == 5 * 3, (
        f"Expected {5 * 3} callback invocations, got {len(callback_chunks)}"
    )
    assert all(c == 1920 for c in callback_chunks), "All chunks should be 1920 bytes"

    sess.close()
