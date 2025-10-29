"""Hotkey runner for the cleaner application."""

from __future__ import annotations

import logging
import threading
from typing import Callable

import keyboard

from .cleanup import delete_folder_contents, empty_recycle_bin
from .config import CleanerConfig

LOGGER = logging.getLogger(__name__)


class _CleanupTask:
    """Serialise cleanup requests so only one runs at a time."""

    def __init__(self, action: Callable[[], None]) -> None:
        self._action = action
        self._lock = threading.Lock()

    def trigger(self) -> None:
        if not self._lock.acquire(blocking=False):
            LOGGER.warning("Cleanup already in progress; ignoring additional hotkey press.")
            return

        thread = threading.Thread(target=self._run, name="cleaner-task", daemon=True)
        thread.start()

    def _run(self) -> None:
        try:
            self._action()
        except Exception:  # pragma: no cover - best effort logging
            LOGGER.exception("Cleanup failed.")
        finally:
            self._lock.release()


def start_hotkey_listener(config: CleanerConfig) -> None:
    """Start listening for the configured hotkey and execute the cleanup."""

    LOGGER.info("Hotkey '%s' armed. Target folder: %s", config.hotkey, config.folder)
    LOGGER.info("Press CTRL+C in this window to stop the listener.")

    def action() -> None:
        LOGGER.info("Hotkey pressed; starting cleanup.")
        delete_folder_contents(
            config.folder,
            send_to_recycle_bin=config.send_to_recycle_bin,
            delete_folder_itself=config.delete_folder_itself,
            recreate_folder=config.recreate_folder,
        )
        if config.empty_recycle_bin:
            try:
                empty_recycle_bin(silent=config.suppress_notifications)
            except OSError as exc:
                LOGGER.error("Failed to empty the Recycle Bin: %s", exc)
        LOGGER.info("Cleanup completed.")

    task = _CleanupTask(action)
    keyboard.add_hotkey(config.hotkey, task.trigger, suppress=False)

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        LOGGER.info("Listener stopped by user.")
