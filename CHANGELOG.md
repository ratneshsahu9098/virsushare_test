# Changelog

All notable changes to virusShare are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Windows installer: Inno Setup script (`installer/virusShare.iss`) produces
  `dist\virusShare-Setup.exe` — installs to Program Files, Start Menu
  shortcut, Add/Remove Programs entry, optional desktop icon, per-machine
  app id; uninstall removes the program and leaves user data alone.
- Portable single-file build kept as an optional target
  (`virusShare_onefile.spec` → `dist\virusShare.exe`).

### Changed

- Packaging switched from single-file to **onedir** (`virusShare.spec` →
  `dist\virusShare\virusShare.exe` + `_internal\`): instant start-up, and
  the layout the installer packages.
- Data directory moved from `%APPDATA%\virusShare` (roaming) to
  `%LOCALAPPDATA%\virusShare` (local): settings, identity, trust store,
  `data\history.db` and `logs\`. One-time migration runs on startup
  (`migrate_legacy_data_dir` / `migrate_roaming_data_dir`); override with
  `VIRUSSHARE_DATA_DIR`.
- Build assets relocated: `assets/virusShare.ico` →
  `resources/icons/virusShare.ico`, `assets/version_info.txt` →
  `resources/version_info.txt`.
- Windows version resource now uses dotted four-part versions
  (File/Product `1.0.0.0`) with correct FileDescription/CompanyName/
  OriginalFilename/Copyright.
- `build_windows.bat` rewritten: venv bootstrap, dependency install,
  clean, full test gate, asset generation, PyInstaller, `--version`
  verification, Inno Setup compile and output-size check.

### Fixed

- Full test-suite native crash in `QCoreApplication::notifyInternal2`:
  Python's cyclic GC could destroy live Qt windows (and their armed
  timers) while Qt was dispatching an event — a use-after-free. The
  collector is now suspended around `app.exec()`/shutdown (`app.py`) and
  between tests (`conftest.py`), with explicit collections at safe points.

## [1.0.0] - 2026-09-29

First complete release.

### Added

- UDP broadcast discovery with 10 s expiry, lost-device detection and manual
  **Connect to IP…** fallback.
- Pairing with 6-digit codes (SHA-256 of certificate fingerprints), trust
  store with revocation from the device panel.
- TLS-encrypted transfers (ECDSA P-256, per-session or whole-session toggle),
  streaming SHA-256 verification on both ends.
- Pause / resume / cancel with chunk-aligned resume from `.etherpartial`
  files across pauses, drops and restarts; conflict dialog with
  skip / replace / keep-both / cancel and apply-to-all.
- Bounded reconnect, send-side concurrency slots, CANCEL propagation.
- SQLite transfer history with search and pruning.
- PySide6 GUI: device list, transfer queue with animated progress bars,
  drag & drop to send, in-window toasts, empty states, light/dark/system
  themes, pairing/conflict/settings/history dialogs, system tray with
  minimize-to-tray and balloon notifications.
- End-to-end tests over real loopback (pair, transfer, resume, unicode
  paths, conflicts, late receivers).
- PyInstaller packaging: single-file windowed exe with branded icon and
  Windows version resource; `build_windows.bat` runs the test suite before
  building.
- `--version` CLI flag; Help → About shows Qt/Python/data locations.
- Sender/Receiver mode selection: a start screen with **Send Files** /
  **Receive Files** cards; a sender screen (live receiver list with single
  selection, Manual IP dialog, drop zone + Add Files/Add Folder staging,
  Send button gated on device + files); a receiver screen (machine name,
  IP, link speed, save location with Change Location, waiting status).

### Changed

- Renamed the application to **virusShare**: window/tray titles, exe name,
  log file, `%APPDATA%\virusShare` data dir and the HKCU Run autostart key.
  Existing installs migrate automatically — the old data directory is
  renamed once on startup and the legacy autostart entry is removed.

### Security

- Traversal-proof path handling (absolute paths, `..`, UNC, drive letters,
  reserved names, alternate data streams, symlink escapes all rejected).
- Certificate fingerprint pinning: trust does not silently survive a
  certificate rotation — the device must be paired again.
