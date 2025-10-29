# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

project_root = Path(__file__).resolve().parent.parent
script_path = project_root / "cleaner" / "__main__.py"
config_example = project_root / "config.example.json"

a = Analysis(
    [str(script_path)],
    pathex=[str(project_root)],
    binaries=[],
    datas=[(str(config_example), 'resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='hotkey-cleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hotkey-cleaner'
)
