"""Pytest fixtures, rootdir marker, and logging level gate.

An empty conftest.py at tests/ is the canonical SciTeX
convention (audit-project PS208) — it pins the pytest
rootdir and gives downstream fixtures a home.

Log level for capture tests: scitex-logging reads SCITEX_LOGGING_LEVEL
once at import (default INFO, but dev shells often export warning). INFO is
needed so log.info lines reach capsys; setdefault keeps an explicit value.
"""

from __future__ import annotations

import os

# Log level for capture tests: scitex-logging reads SCITEX_LOGGING_LEVEL
# once at import (default INFO, but dev shells often export warning). INFO is
# needed so log.info lines reach capsys; setdefault keeps an explicit value.
os.environ.setdefault("SCITEX_LOGGING_LEVEL", "INFO")

try:
    import scitex_logging as _slogging

    _slogging.set_level("INFO")
except Exception:
    pass
