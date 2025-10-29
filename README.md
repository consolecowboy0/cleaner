# Cleaner Hotkey Utility

This repository provides a small Python utility that listens for a global hotkey on
Windows and, when pressed, removes the contents of a designated folder before
optionally emptying the Recycle Bin. This is useful when working with large
video files or other temporary artefacts that consume significant disk space.

> ⚠️ The script is designed for Windows 10 or newer. The hotkey listener relies
> on the [`keyboard`](https://pypi.org/project/keyboard/) library, which needs to
> be executed with administrative privileges on Windows to capture system-wide
> key presses.

## Features

- Global hotkey trigger (default: <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Delete</kbd>).
- Delete only the folder contents or the folder itself.
- Choose between permanently deleting files or sending them to the Recycle Bin.
- Automatically empty the Recycle Bin using the Windows Shell API.
- Automatically recreate the target folder after cleanup.

## Download a ready-made executable

Every push and pull request to the `main` branch triggers a GitHub Actions
workflow that builds a portable Windows executable with PyInstaller and uploads
it as a downloadable artifact. After the workflow finishes, open the **Actions**
tab for the relevant run, select the *Build Windows executable* workflow, and
download the `hotkey-cleaner-windows` artifact. The ZIP file contains
`hotkey-cleaner.exe` and a copy of `config.example.json` so you can get started
immediately on Windows 10 or newer without installing Python.

## Installation

1. Ensure you have Python 3.9 or newer installed on your Windows machine.
2. Clone this repository and open a terminal in the project directory.
3. (Optional but recommended) Create and activate a virtual environment.
4. Install the required dependencies:

 ```powershell
  py -m pip install -r requirements.txt
  ```

If you would like to build the Windows executable yourself, also install the
developer requirements and run the packaging helper:

```powershell
py -m pip install -r requirements-dev.txt
py scripts/build_exe.py
```

The script invokes PyInstaller using the bundled spec file and creates
`dist/hotkey-cleaner.zip`, which matches the artifact produced by the automated
workflow.

## Configuration

Copy the example configuration file and adjust it to match your setup:

```powershell
Copy-Item config.example.json config.json
```

`config.json` contains the following options:

- `folder`: Absolute or relative path to the folder that should be cleaned.
- `hotkey`: Combination understood by the `keyboard` library (for example,
  `ctrl+alt+f`).
- `send_to_recycle_bin`: Set to `true` to move files to the Recycle Bin instead
  of permanently deleting them.
- `empty_recycle_bin`: Set to `true` to empty the Recycle Bin after the folder is
  cleared.
- `delete_folder_itself`: Set to `true` if the folder itself should be removed.
- `recreate_folder`: Set to `false` to avoid re-creating the folder after
  deletion.
- `suppress_notifications`: Set to `true` to avoid visual or audio shell
  notifications when emptying the Recycle Bin.

## Usage

Run the listener with:

```powershell
py -m cleaner --config config.json
```

Additional command-line options allow you to override configuration values
without editing the JSON file:

- `--folder <PATH>`: Override the target folder.
- `--hotkey <KEYS>`: Override the hotkey combination.
- `--permanent`: Force permanent deletion even if the configuration says
  otherwise.
- `--no-recycle-empty`: Skip emptying the Recycle Bin.
- `--delete-folder`: Delete the folder itself instead of just its contents.
- `--no-recreate`: Do not recreate the folder after deletion.
- `--verbose`: Enable debug-level logging output.

Leave the terminal window running in the background. Whenever you press the
configured hotkey, the cleanup routine runs. Press <kbd>Ctrl</kbd> + <kbd>C</kbd>
inside the terminal to stop the listener.

## Safety Tips

- Start by pointing the tool at a throwaway folder to verify the behaviour
  matches your expectations.
- Consider disabling `empty_recycle_bin` until you are confident everything is
  being deleted correctly.
- Keep regular backups of important files to guard against accidental deletion.
