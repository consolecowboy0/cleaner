import sys
import threading
import time
from pathlib import Path
from types import ModuleType


if "keyboard" not in sys.modules:
    keyboard_stub = ModuleType("keyboard")
    keyboard_stub.add_hotkey = lambda *args, **kwargs: None
    keyboard_stub.wait = lambda *args, **kwargs: None
    sys.modules["keyboard"] = keyboard_stub

from cleaner.config import CleanerConfig
from cleaner.runner import _CleanupTask
from cleaner.__main__ import apply_overrides


class _ActionRecorder:
    def __init__(self):
        self.events = []
        self._event = threading.Event()

    def __call__(self):
        self.events.append("start")
        self._event.wait(timeout=1)
        self.events.append("end")

    def release(self):
        self._event.set()


def test_cleanup_task_serialises_execution():
    recorder = _ActionRecorder()
    task = _CleanupTask(recorder)

    task.trigger()
    time.sleep(0.05)
    task.trigger()

    assert recorder.events == ["start"]

    recorder.release()
    time.sleep(0.05)
    assert recorder.events == ["start", "end"]


def test_apply_overrides_updates_config(tmp_path):
    base = CleanerConfig(
        folder=tmp_path,
        hotkey="ctrl+alt+x",
        send_to_recycle_bin=True,
        empty_recycle_bin=True,
        delete_folder_itself=False,
        recreate_folder=True,
        suppress_notifications=False,
    )

    args = type(
        "Args",
        (),
        {
            "folder": Path("relative"),
            "hotkey": "ctrl+shift+y",
            "permanent": True,
            "no_recycle_empty": True,
            "delete_folder": True,
            "no_recreate": True,
        },
    )()

    new_config = apply_overrides(base, args)

    assert new_config.folder == (Path.cwd() / "relative").resolve()
    assert new_config.hotkey == "ctrl+shift+y"
    assert new_config.send_to_recycle_bin is False
    assert new_config.empty_recycle_bin is False
    assert new_config.delete_folder_itself is True
    assert new_config.recreate_folder is False
    assert new_config.suppress_notifications is False
