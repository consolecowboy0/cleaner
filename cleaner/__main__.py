"""Command line interface for the cleaner application."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from . import load_config, start_hotkey_listener
from .config import CleanerConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hotkey-triggered folder cleaner")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.json"),
        help="Path to the configuration JSON file (default: ./config.json)",
    )
    parser.add_argument(
        "--folder",
        type=Path,
        help="Override the folder configured in the JSON file.",
    )
    parser.add_argument(
        "--hotkey",
        type=str,
        help="Override the configured hotkey (for example, 'ctrl+alt+f').",
    )
    parser.add_argument(
        "--permanent",
        action="store_true",
        help="Permanently delete files instead of sending them to the Recycle Bin.",
    )
    parser.add_argument(
        "--no-recycle-empty",
        action="store_true",
        help="Do not empty the Recycle Bin after deleting the folder.",
    )
    parser.add_argument(
        "--delete-folder",
        action="store_true",
        help="Delete the folder itself instead of just its contents.",
    )
    parser.add_argument(
        "--no-recreate",
        action="store_true",
        help="Do not recreate the folder after deleting it.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def apply_overrides(config: CleanerConfig, args: argparse.Namespace) -> CleanerConfig:
    folder = config.folder
    if args.folder is not None:
        folder = args.folder.expanduser()
        if not folder.is_absolute():
            folder = (Path.cwd() / folder).resolve()

    hotkey = args.hotkey or config.hotkey

    send_to_recycle_bin = config.send_to_recycle_bin
    if args.permanent:
        send_to_recycle_bin = False

    empty_recycle_bin = config.empty_recycle_bin
    if args.no_recycle_empty:
        empty_recycle_bin = False

    delete_folder_itself = config.delete_folder_itself or args.delete_folder
    recreate_folder = config.recreate_folder and not args.no_recreate

    return CleanerConfig(
        folder=folder,
        hotkey=hotkey,
        send_to_recycle_bin=send_to_recycle_bin,
        empty_recycle_bin=empty_recycle_bin,
        delete_folder_itself=delete_folder_itself,
        recreate_folder=recreate_folder,
        suppress_notifications=config.suppress_notifications,
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    config = load_config(args.config)
    config = apply_overrides(config, args)

    start_hotkey_listener(config)


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
