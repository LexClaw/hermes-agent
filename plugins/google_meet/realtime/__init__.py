"""Realtime speech subpackage for the google_meet plugin (v2).

Provides a thin Cartesia TTS client and a file-queue speaker
wrapper so the Meet bot can play synthesized speech through the
virtual audio bridge.
"""

from .cartesia_client import CartesiaSession  # noqa: F401

__all__ = ["CartesiaSession"]
