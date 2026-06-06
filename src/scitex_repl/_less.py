#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""less — pipe a string to ``less`` from inside an IPython session.

Ported from scitex-gen ``_ipython/_less.py``.
"""
from __future__ import annotations


def less(output: str) -> None:
    """Display ``output`` using the system ``less`` pager.

    Writes ``output`` to a temp file and invokes ``less`` via the
    IPython shell's ``system`` hook (so it inherits the parent
    terminal). Removes the temp file when ``less`` exits.

    Parameters
    ----------
    output : str
        Text to display.

    Notes
    -----
    Requires ``IPython`` (``less`` uses ``IPython.get_ipython().system``
    to inherit the parent terminal correctly).
    """
    import os
    import tempfile

    from IPython import get_ipython

    with tempfile.NamedTemporaryFile(delete=False, mode="w+t") as tmpfile:
        tmpfile.write(output)
        tmpfile_name = tmpfile.name

    get_ipython().system(f"less {tmpfile_name}")
    os.remove(tmpfile_name)
