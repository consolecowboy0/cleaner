"""Cleaner hotkey application."""

from __future__ import annotations

from .config import CleanerConfig, load_config

__all__ = ["CleanerConfig", "load_config", "start_hotkey_listener"]


def start_hotkey_listener(config: CleanerConfig) -> None:
    """Import the hotkey runner lazily to avoid heavy dependencies at import time."""

    from .runner import start_hotkey_listener as _start_hotkey_listener

    _start_hotkey_listener(config)
