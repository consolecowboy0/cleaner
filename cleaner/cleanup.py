"""Cleanup routines for removing folders and emptying the recycle bin."""

from __future__ import annotations

import ctypes
import logging
import shutil
from pathlib import Path
from typing import Iterable

try:
    from send2trash import send2trash
except ImportError:  # pragma: no cover - dependency should be installed by the user
    send2trash = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)


def _iter_children(folder: Path) -> Iterable[Path]:
    if not folder.exists():
        return []
    try:
        return list(folder.iterdir())
    except PermissionError as exc:
        raise PermissionError(f"Unable to read contents of '{folder}': {exc}") from exc


def delete_folder_contents(
    folder: Path,
    *,
    send_to_recycle_bin: bool,
    delete_folder_itself: bool,
    recreate_folder: bool,
) -> None:
    """Delete the contents of *folder* using the configured strategy."""

    folder = folder.resolve()
    if not folder.exists():
        LOGGER.info("Folder '%s' does not exist; nothing to delete.", folder)
        if recreate_folder:
            LOGGER.debug("Creating missing folder '%s'.", folder)
            folder.mkdir(parents=True, exist_ok=True)
        return

    LOGGER.info("Removing %s of '%s'.", "folder" if delete_folder_itself else "contents", folder)

    if delete_folder_itself:
        _delete_path(
            folder,
            send_to_recycle_bin=send_to_recycle_bin,
        )
        if recreate_folder:
            LOGGER.debug("Recreating folder '%s'.", folder)
            folder.mkdir(parents=True, exist_ok=True)
        return

    for child in _iter_children(folder):
        _delete_path(child, send_to_recycle_bin=send_to_recycle_bin)


def _delete_path(path: Path, *, send_to_recycle_bin: bool) -> None:
    if send_to_recycle_bin:
        if send2trash is None:
            raise RuntimeError(
                "send2trash is not installed; cannot move files to the Recycle Bin."
            )
        LOGGER.debug("Sending '%s' to the Recycle Bin.", path)
        send2trash(str(path))
    else:
        if path.is_dir() and not path.is_symlink():
            LOGGER.debug("Recursively deleting directory '%s'.", path)
            shutil.rmtree(path)
        else:
            LOGGER.debug("Deleting file '%s'.", path)
            path.unlink(missing_ok=True)


_SHERB_NOCONFIRMATION = 0x00000001
_SHERB_NOPROGRESSUI = 0x00000002
_SHERB_NOSOUND = 0x00000004


def empty_recycle_bin(*, silent: bool = True) -> None:
    """Empty the Windows Recycle Bin using the shell API."""

    if ctypes is None:  # pragma: no cover - ctypes is always available
        raise RuntimeError("ctypes is not available on this interpreter.")

    if not hasattr(ctypes.windll, "shell32"):
        LOGGER.warning("Recycle Bin cleanup is only available on Windows systems.")
        return

    flags = _SHERB_NOCONFIRMATION
    if silent:
        flags |= _SHERB_NOPROGRESSUI | _SHERB_NOSOUND

    shell32 = ctypes.windll.shell32
    result = shell32.SHEmptyRecycleBinW(None, None, flags)
    if result != 0:
        raise OSError(f"SHEmptyRecycleBinW failed with error code {result}")

    LOGGER.info("Recycle Bin emptied successfully.")
