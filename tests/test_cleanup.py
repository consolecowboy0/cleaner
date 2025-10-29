from pathlib import Path

import pytest

import cleaner.cleanup as cleanup


def _create_fixture_directory(tmp_path: Path) -> None:
    (tmp_path / "file.txt").write_text("data")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "nested.txt").write_text("nested")


def test_delete_folder_contents_removes_children(tmp_path):
    _create_fixture_directory(tmp_path)

    cleanup.delete_folder_contents(
        tmp_path,
        send_to_recycle_bin=False,
        delete_folder_itself=False,
        recreate_folder=False,
    )

    assert tmp_path.exists()
    assert not any(tmp_path.iterdir())


def test_delete_folder_itself_and_recreate(tmp_path):
    _create_fixture_directory(tmp_path)

    cleanup.delete_folder_contents(
        tmp_path,
        send_to_recycle_bin=False,
        delete_folder_itself=True,
        recreate_folder=True,
    )

    assert tmp_path.exists()
    assert not any(tmp_path.iterdir())


def test_delete_folder_handles_missing(tmp_path):
    target = tmp_path / "missing"

    cleanup.delete_folder_contents(
        target,
        send_to_recycle_bin=False,
        delete_folder_itself=False,
        recreate_folder=True,
    )

    assert target.exists()


def test_delete_folder_uses_recycle_bin(monkeypatch, tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")
    calls = []

    def fake_send2trash(path_str: str) -> None:
        calls.append(path_str)
        file_path.unlink(missing_ok=True)

    monkeypatch.setattr(cleanup, "send2trash", fake_send2trash)

    cleanup.delete_folder_contents(
        tmp_path,
        send_to_recycle_bin=True,
        delete_folder_itself=False,
        recreate_folder=False,
    )

    assert calls == [str(file_path)]


def test_delete_folder_requires_send2trash(monkeypatch, tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")

    monkeypatch.setattr(cleanup, "send2trash", None)

    with pytest.raises(RuntimeError):
        cleanup.delete_folder_contents(
            tmp_path,
            send_to_recycle_bin=True,
            delete_folder_itself=False,
            recreate_folder=False,
        )


def test_empty_recycle_bin_calls_shell(monkeypatch):
    calls = []

    class DummyShell32:
        def SHEmptyRecycleBinW(self, hwnd, path, flags):
            calls.append((hwnd, path, flags))
            return 0

    class DummyLoader:
        def __init__(self):
            self.shell32 = DummyShell32()

    monkeypatch.setattr(cleanup.ctypes, "windll", DummyLoader(), raising=False)

    cleanup.empty_recycle_bin(silent=False)

    assert calls

