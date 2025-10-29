import json
from pathlib import Path

import pytest

from cleaner.config import CleanerConfig, load_config


def test_from_mapping_resolves_relative_folder(tmp_path, monkeypatch):
    relative = Path("subdir")
    data = {
        "folder": str(relative),
        "hotkey": "ctrl+shift+x",
        "send_to_recycle_bin": True,
        "empty_recycle_bin": False,
        "delete_folder_itself": True,
        "recreate_folder": False,
        "suppress_notifications": True,
    }

    monkeypatch.chdir(tmp_path)
    cfg = CleanerConfig.from_mapping(data)

    assert cfg.folder == (tmp_path / relative).resolve()
    assert cfg.hotkey == "ctrl+shift+x"
    assert cfg.send_to_recycle_bin is True
    assert cfg.empty_recycle_bin is False
    assert cfg.delete_folder_itself is True
    assert cfg.recreate_folder is False
    assert cfg.suppress_notifications is True


def test_to_dict_round_trip(tmp_path):
    cfg = CleanerConfig(
        folder=tmp_path,
        hotkey="alt+h",
        send_to_recycle_bin=True,
        empty_recycle_bin=False,
        delete_folder_itself=True,
        recreate_folder=False,
        suppress_notifications=True,
    )

    serialised = cfg.to_dict()
    restored = CleanerConfig.from_mapping(serialised)

    assert restored.folder == cfg.folder
    assert restored.hotkey == cfg.hotkey
    assert restored.send_to_recycle_bin == cfg.send_to_recycle_bin
    assert restored.empty_recycle_bin == cfg.empty_recycle_bin
    assert restored.delete_folder_itself == cfg.delete_folder_itself
    assert restored.recreate_folder == cfg.recreate_folder
    assert restored.suppress_notifications == cfg.suppress_notifications


def test_load_config_reads_file(tmp_path):
    config_path = tmp_path / "config.json"
    payload = {"folder": str(tmp_path / "target"), "hotkey": "alt+z"}
    config_path.write_text(json.dumps(payload))

    config = load_config(config_path)

    assert config.folder == (tmp_path / "target")
    assert config.hotkey == "alt+z"


def test_load_config_missing_folder_option(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"hotkey": "alt+z"}))

    with pytest.raises(ValueError):
        load_config(config_path)


def test_load_config_rejects_missing_path(tmp_path):
    missing = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_config(missing)


def test_load_config_invalid_json(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("not-json")

    with pytest.raises(ValueError):
        load_config(config_path)
