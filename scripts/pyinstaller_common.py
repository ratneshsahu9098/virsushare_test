"""PyInstaller configuration shared by the virusShare build targets.

Imported by ``virusShare.spec`` (production, onedir) and
``virusShare_onefile.spec`` (portable, single file) so the two targets can
never drift apart.  Everything here is *build-time* only - none of it ships
in the application.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Re-exported for the specs: generate/refresh icon + version resource first.
from scripts.make_release_assets import ensure_assets  # noqa: E402,F401

__all__ = [
    "EXCLUDED_QT",
    "HIDDEN_IMPORTS",
    "analysis_kwargs",
    "bundle_datas",
    "ensure_assets",
]

# Qt modules that are never imported by virusShare; excluding them keeps
# the bundle well below the full PySide6 footprint.
EXCLUDED_QT: List[str] = [
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtQuick",
    "PySide6.QtQuickWidgets",
    "PySide6.QtQml",
    "PySide6.Qt3DCore",
    "PySide6.Qt3DRender",
    "PySide6.Qt3DInput",
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets",
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
    "PySide6.QtSql",
    "PySide6.QtTest",
    "tkinter",
]

# Imported lazily inside functions (spec names them so a --clean build never
# misses them even when the module graph is conservative).
HIDDEN_IMPORTS: List[str] = [
    "gui.bridge",
    "gui.styles",
    "gui.icons",
    "gui.device_panel",
    "gui.transfer_queue",
    "gui.role_screen",
    "gui.sender_screen",
    "gui.receiver_screen",
    "gui.pairing_dialog",
    "gui.conflict_dialog",
    "gui.history_dialog",
    "gui.settings_dialog",
    "gui.tray",
    "gui.main_window",
    "database.history",
    "transfer.manager",
    "utils.windows",
    "utils.network",
    "utils.formatting",
    "utils.logger",
]


def bundle_datas() -> List[tuple]:
    """Data files shipped next to the code (``resources/``: icon, version).

    Nothing user-writable belongs here - settings, identity, trust store,
    history and logs all live under ``%LOCALAPPDATA%\\virusShare`` at runtime.
    """
    datas: List[tuple] = []
    resources = ROOT / "resources"
    if resources.is_dir():
        for name in sorted(os.listdir(resources)):
            source = resources / name
            datas.append((str(source), "resources"))
    return datas


def analysis_kwargs() -> Dict:
    """Keyword arguments common to every ``Analysis`` in this project."""
    return {
        "pathex": [str(ROOT)],
        "binaries": [],
        "datas": bundle_datas(),
        "hiddenimports": HIDDEN_IMPORTS,
        "hookspath": [],
        "hooksconfig": {},
        "runtime_hooks": [],
        "excludes": EXCLUDED_QT,
        "noarchive": False,
    }
