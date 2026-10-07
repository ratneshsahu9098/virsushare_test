"""virusShare - Core Constants and Configuration"""

import logging
import os
import shutil
import time
from pathlib import Path

log = logging.getLogger(__name__)

APP_NAME = "virusShare"
APP_VERSION = "1.0.0"
APP_AUTHOR = "virusShare"

# Data directory used before the rename; migrated once by
# ``migrate_legacy_data_dir`` so existing identities/trust/history survive.
LEGACY_APP_NAME = "EtherTransfer"

DISCOVERY_PORT = 54321
TRANSFER_PORT = 54322
CONTROL_PORT = 54323

BROADCAST_INTERVAL = 2.0
DISCOVERY_TIMEOUT = 10.0
CONNECTION_TIMEOUT = 15.0
TRANSFER_CHUNK_SIZE = 64 * 1024
CHECKSUM_CHUNK_SIZE = 1024 * 1024

MAGIC_BYTES = b"ETHR"
PROTOCOL_VERSION = 1

# --------------------------------------------------------------------------- #
# Transfer tuning
# --------------------------------------------------------------------------- #

# Chunk size used by the sender for FILE_CHUNK messages.  1 MiB balances
# syscall overhead against memory use on 1..10 Gbps links and stays far
# below the 32 MiB protocol payload cap.  Configurable via settings.
SEND_CHUNK_SIZE = 1024 * 1024
MIN_SEND_CHUNK_SIZE = 64 * 1024
MAX_SEND_CHUNK_SIZE = 8 * 1024 * 1024

# Sockets block on control messages (manifest approval, pairing dialogs) for
# at most this long before the peer is considered dead.
CONTROL_MESSAGE_TIMEOUT = 180.0
HANDSHAKE_TIMEOUT = 30.0
PAIRING_TIMEOUT = 60.0

# Partial (incomplete) files are never written under their final name.
PARTIAL_SUFFIX = ".etherpartial"
PARTIAL_META_SUFFIX = ".etherpartial.json"

MAX_FILENAME_LENGTH = 200
MAX_RELATIVE_PATH_LENGTH = 400

MESSAGE_TYPES = {
    "DISCOVERY": 0x01,
    "DISCOVERY_RESPONSE": 0x02,
    "CONNECT_REQUEST": 0x10,
    "CONNECT_RESPONSE": 0x11,
    "DISCONNECT": 0x12,
    "SESSION_CHALLENGE": 0x13,
    "PAIR_CONFIRM": 0x14,
    "FILE_LIST": 0x20,
    "FILE_REQUEST": 0x21,
    "FILE_DATA": 0x22,
    "FILE_CHUNK": 0x23,
    "FILE_COMPLETE": 0x24,
    "FILE_CANCEL": 0x25,
    "FILE_RESUME": 0x26,
    "CHECKSUM_REQUEST": 0x30,
    "CHECKSUM_RESPONSE": 0x31,
    "ERROR": 0xFF,
}

ERROR_CODES = {
    0x01: "Connection refused",
    0x02: "File not found",
    0x03: "Permission denied",
    0x04: "Disk full",
    0x05: "Checksum mismatch",
    0x06: "Protocol error",
    0x07: "Timeout",
    0x08: "Cancelled by user",
    0x09: "Encryption error",
}

DEFAULT_SETTINGS = {
    "auto_accept_trusted": False,
    "enable_encryption": True,
    "transfer_port": TRANSFER_PORT,
    "discovery_port": DISCOVERY_PORT,
    "max_concurrent_transfers": 3,
    "reconnect_attempts": 3,
    "buffer_size": TRANSFER_CHUNK_SIZE,
    "verify_checksums": True,
    "save_received_files_to": str(Path.home() / "Downloads" / APP_NAME),
    "trusted_devices": [],
    "theme": "system",
    "language": "en",
    "minimize_to_tray": True,
    "show_notifications": True,
    "start_with_windows": False,
    "preferred_network_adapter": "auto",
    "require_connection_approval": True,
    "chunk_size": SEND_CHUNK_SIZE,
}

def get_app_data_dir() -> Path:
    """Per-user, non-roaming application data directory.

    ``%LOCALAPPDATA%\\virusShare`` by default.  Deliberately *not* next to the
    executable: an installed copy lives in ``C:\\Program Files\\virusShare``,
    which is read-only for normal users, so no database, log, config or lock
    file is ever written into the install directory (or anywhere the exe
    happens to be unpacked to).  "Local" rather than "Roaming" because the
    SQLite history, the identity key and partial transfers are
    machine-specific and must not follow a user across machines.

    Overridable with ``VIRUSSHARE_DATA_DIR`` (tests, portable installs).
    """
    override = os.environ.get("VIRUSSHARE_DATA_DIR")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or str(
        Path.home() / "AppData" / "Local"
    )
    return Path(base) / APP_NAME


def get_data_dir() -> Path:
    """Database sub-directory (``%LOCALAPPDATA%\\virusShare\\data``)."""
    return get_app_data_dir() / "data"


def get_settings_path() -> Path:
    """Get the settings file path."""
    return get_app_data_dir() / "settings.json"


def get_logs_dir() -> Path:
    """Get the logs directory."""
    return get_app_data_dir() / "logs"


def get_trust_store_path() -> Path:
    """Get the trusted-device store path."""
    return get_app_data_dir() / "trusted_devices.json"


def get_history_db_path() -> Path:
    """Get the SQLite transfer-history database path."""
    return get_data_dir() / "history.db"

def get_identity_path() -> Path:
    """Get the long-term identity (certificate + private key) path."""
    return get_app_data_dir() / "identity.pem"

def _relocate(old: Path, new: Path) -> None:
    """Move directory ``old`` to ``new`` (rename with copy fallback).

    A rename that fails (antivirus lock, transient permissions) must not be
    swallowed: the caller would see ``new.exists()`` right after and could
    skip the migration forever, orphaning the legacy identity/trust/history
    (M29).  Retries cover transient locks; a persistent failure falls back to
    copying the content.
    """
    if not old.is_dir() or new.exists() or old == new:
        return
    new.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        try:
            old.rename(new)
            return
        except OSError:
            if attempt == 3:
                break
            time.sleep(0.05)
    try:
        shutil.copytree(old, new)
    except OSError:
        log.exception("data dir migration failed for %s -> %s", old, new)
        return
    log.error(
        "data dir rename failed; copied %s -> %s instead",
        old,
        new,
    )


def migrate_legacy_data_dir() -> None:
    """One-time rename of the pre-rebrand data directory (best effort).

    ``EtherTransfer`` (the old name) is moved next to the *current* data
    directory, so an upgraded install keeps its identity, trust store and
    history.  A no-op when either side is missing.
    """
    try:
        new = get_app_data_dir()
        old = new.parent / LEGACY_APP_NAME
        _relocate(old, new)
    except OSError:
        log.exception("legacy data dir migration failed")


def migrate_roaming_data_dir() -> None:
    """One-time move from the old roaming location to ``%LOCALAPPDATA%``.

    Earlier versions stored everything in ``%APPDATA%\\virusShare`` (roaming).
    The data is machine-specific (identity key, SQLite history, partial
    transfers), so it is relocated to ``%LOCALAPPDATA%\\virusShare`` once, and
    the history database is then normalized into the ``data/`` sub-directory
    that ``get_history_db_path`` expects.  Never touches the destination if it
    already exists, and is a no-op when source and destination coincide.
    """
    try:
        new = get_app_data_dir()
        roaming_base = Path(
            os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
        )
        _relocate(roaming_base / APP_NAME, new)
        # normalize history.db -> data/history.db (old layout)
        old_db = new / "history.db"
        new_db = get_history_db_path()
        if old_db.is_file() and not new_db.exists():
            new_db.parent.mkdir(parents=True, exist_ok=True)
            try:
                old_db.rename(new_db)
            except OSError:
                log.exception("history db move to data/ failed")
    except OSError:
        log.exception("roaming data dir migration failed")


def ensure_dirs():
    """Ensure all required directories exist."""
    migrate_legacy_data_dir()
    migrate_roaming_data_dir()
    get_app_data_dir().mkdir(parents=True, exist_ok=True)
    get_data_dir().mkdir(parents=True, exist_ok=True)
    get_logs_dir().mkdir(parents=True, exist_ok=True)
    Path(DEFAULT_SETTINGS["save_received_files_to"]).mkdir(parents=True, exist_ok=True)