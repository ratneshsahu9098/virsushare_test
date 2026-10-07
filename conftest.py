import gc
import os
import sys
from pathlib import Path

# GUI tests must never open real windows - do this before any Qt import.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _keep_gc_out_of_event_dispatch():
    """Keep the cyclic GC out of Qt event dispatch for the whole session.

    Widgets form reference cycles (parent/child wrappers, signal closures),
    so their destruction is deferred to the cyclic GC.  A collection that
    lands while a later test pumps Qt events tears down whole window trees -
    armed timers included - inside Qt's timer dispatch, which then reads
    freed objects and crashes the process (0xC0000005 in
    QCoreApplication::notifyInternal2).

    Automatic collection is therefore disabled for the session and run
    explicitly at test boundaries instead, where no Qt event is in flight.
    Refcount-based destruction is unaffected.
    """
    gc.disable()
    yield
    gc.enable()
    gc.collect()


@pytest.fixture(autouse=True)
def _collect_gui_garbage_between_tests():
    """Run the cyclic GC between tests, never during event dispatch."""
    gc.collect()
    yield
    gc.collect()
