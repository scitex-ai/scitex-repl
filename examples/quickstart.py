"""scitex-repl quickstart: paste the clipboard, page with less, embed a shell.

``paste()`` execs whatever the clipboard holds, so this demo swaps in a
harmless stub clipboard first — never point paste() at untrusted data.
``less()`` and ``embed()`` need a real terminal; they are shown but only
run when ``--interactive`` is passed.
"""

from __future__ import annotations

import sys
import types


def main(interactive: bool = False) -> None:
    import scitex_repl

    print("public surface:", sorted(scitex_repl.__all__))

    # paste() with a harmless stub clipboard (no display needed).
    stub = types.ModuleType("pyperclip")
    setattr(stub, "paste", lambda: "demo_result = 6 * 7\n")
    setattr(stub, "PyperclipException", Exception)
    sys.modules["pyperclip"] = stub
    scitex_repl.paste()
    print("paste() executed the stub clipboard without error")

    if interactive:
        scitex_repl.less("\n".join(f"line {i}" for i in range(200)))
        scitex_repl.embed()


if __name__ == "__main__":
    main(interactive="--interactive" in sys.argv[1:])
