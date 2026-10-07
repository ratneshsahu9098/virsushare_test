# -*- mode: python ; coding: utf-8 -*-
"""virusShare - portable build (onefile) -> single exe.

Build from the repository root:

    python -m PyInstaller --clean --noconfirm virusShare_onefile.spec

Produces ``dist\\virusShare.exe``: a self-contained archive that unpacks to a
temp directory on start (slower start-up than the onedir build).  Kept as an
optional extra - the supported distribution remains the onedir build plus
the installer.  User data still lives in ``%LOCALAPPDATA%\\virusShare`` and is
never written next to (or inside) the archive.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.abspath(SPEC))  # noqa: F821
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.pyinstaller_common import analysis_kwargs, ensure_assets  # noqa: E402

ICON_FILE, VERSION_FILE = ensure_assets()

a = Analysis(  # noqa: F821
    ["app.py"],
    **analysis_kwargs(),
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="virusShare",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,     # unpack to the system temp dir
    console=False,           # windowed app: no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE,
    version=VERSION_FILE,
)
