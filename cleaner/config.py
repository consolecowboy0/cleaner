"""Configuration helpers for the cleaner application."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class CleanerConfig:
    """Settings that drive the cleaner hotkey application."""

    folder: Path
    hotkey: str = "ctrl+alt+delete"
    send_to_recycle_bin: bool = False
    empty_recycle_bin: bool = True
    delete_folder_itself: bool = False
    recreate_folder: bool = True
    suppress_notifications: bool = False

    @classmethod
    def from_mapping(cls, data: Dict[str, Any]) -> "CleanerConfig":
        """Create a configuration instance from a dictionary."""

        folder_value = data.get("folder")
        if not folder_value:
            raise ValueError("Configuration is missing the 'folder' option.")

        folder_path = Path(folder_value).expanduser()
        if not folder_path.is_absolute():
            folder_path = (Path.cwd() / folder_path).resolve()

        hotkey = data.get("hotkey", cls.hotkey)
        send_to_recycle_bin = bool(data.get("send_to_recycle_bin", cls.send_to_recycle_bin))
        empty_recycle_bin = bool(data.get("empty_recycle_bin", cls.empty_recycle_bin))
        delete_folder_itself = bool(data.get("delete_folder_itself", cls.delete_folder_itself))
        recreate_folder = bool(data.get("recreate_folder", cls.recreate_folder))
        suppress_notifications = bool(data.get("suppress_notifications", cls.suppress_notifications))

        return cls(
            folder=folder_path,
            hotkey=hotkey,
            send_to_recycle_bin=send_to_recycle_bin,
            empty_recycle_bin=empty_recycle_bin,
            delete_folder_itself=delete_folder_itself,
            recreate_folder=recreate_folder,
            suppress_notifications=suppress_notifications,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON serialisable representation of the configuration."""

        return {
            "folder": str(self.folder),
            "hotkey": self.hotkey,
            "send_to_recycle_bin": self.send_to_recycle_bin,
            "empty_recycle_bin": self.empty_recycle_bin,
            "delete_folder_itself": self.delete_folder_itself,
            "recreate_folder": self.recreate_folder,
            "suppress_notifications": self.suppress_notifications,
        }


def load_config(path: Optional[Path]) -> CleanerConfig:
    """Load configuration from *path* or fall back to defaults."""

    if path is None:
        raise ValueError("A configuration file path must be provided.")

    path = Path(path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Configuration file '{path}' was not found.")

    with path.open("r", encoding="utf-8") as handle:
        try:
            payload: Dict[str, Any] = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Configuration file '{path}' is not valid JSON: {exc}") from exc

    config = CleanerConfig.from_mapping(payload)
    logging.debug("Loaded configuration: %s", config)
    return config
