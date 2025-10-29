"""Build utilities for producing a Windows executable with PyInstaller."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"
SPEC_PATH = REPO_ROOT / "packaging" / "hotkey_cleaner.spec"
OUTPUT_NAME = "hotkey-cleaner"
ZIP_BUNDLE = DIST_DIR / f"{OUTPUT_NAME}.zip"


def run_pyinstaller() -> None:
    """Invoke PyInstaller using the bundled spec file."""

    if not SPEC_PATH.exists():
        raise FileNotFoundError(f"Unable to locate spec file at {SPEC_PATH}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        str(SPEC_PATH),
    ]
    subprocess.run(cmd, check=True)


def bundle_artifact() -> Path:
    """Zip the generated executable and companion files for easy download."""

    executable_path = DIST_DIR / OUTPUT_NAME / f"{OUTPUT_NAME}.exe"
    if not executable_path.exists():
        raise FileNotFoundError(
            "Expected executable was not produced. Did PyInstaller run successfully?"
        )

    bundle_root = DIST_DIR / OUTPUT_NAME
    archive_staging = DIST_DIR / f"{OUTPUT_NAME}-bundle"
    if archive_staging.exists():
        shutil.rmtree(archive_staging)
    shutil.copytree(bundle_root, archive_staging)

    # Include the example configuration alongside the binary for convenience.
    example_config = REPO_ROOT / "config.example.json"
    shutil.copy2(example_config, archive_staging / "config.example.json")

    if ZIP_BUNDLE.exists():
        ZIP_BUNDLE.unlink()
    shutil.make_archive(str(ZIP_BUNDLE.with_suffix("")), "zip", archive_staging)
    shutil.rmtree(archive_staging)
    return ZIP_BUNDLE


def main() -> None:
    run_pyinstaller()
    archive = bundle_artifact()
    print(f"Packaged executable available at: {archive}")


if __name__ == "__main__":
    main()
