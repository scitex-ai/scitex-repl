"""Exercise real IPython namespace behavior without opening a terminal/clipboard."""

from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.mark.parametrize("reply,expected", [(" Y ", 42), ("n", None)])
def test_clipboard_executes_only_after_confirmation_before_interaction(
    monkeypatch, capsys, reply, expected
):
    import pyperclip
    from IPython.terminal.embed import InteractiveShellEmbed

    from scitex_repl import embed

    seen = []

    def interact(shell, *args, **kwargs):
        seen.append(kwargs.get("local_ns", shell.user_ns).get("clipboard_result"))
        # This is the real callable's return contract, not a fake returned shell.
        return None

    monkeypatch.setattr(pyperclip, "paste", lambda: "clipboard_result = 6 * 7")
    monkeypatch.setattr("builtins.input", lambda: reply)
    monkeypatch.setattr(InteractiveShellEmbed, "__call__", interact)

    result = embed()

    assert result is None
    assert seen == [expected]
    assert "Do you want to execute it? [y/n]" in capsys.readouterr().out


def test_unavailable_clipboard_still_opens_an_empty_confirmed_shell(monkeypatch):
    import pyperclip
    from IPython.terminal.embed import InteractiveShellEmbed

    from scitex_repl import embed

    seen = []

    def unavailable():
        raise pyperclip.PyperclipException("synthetic unavailable clipboard")

    monkeypatch.setattr(pyperclip, "paste", unavailable)
    monkeypatch.setattr("builtins.input", lambda: "y")
    monkeypatch.setattr(
        InteractiveShellEmbed,
        "__call__",
        lambda shell, **kwargs: seen.append(
            kwargs.get("local_ns", shell.user_ns).get("clipboard_result")
        ),
    )

    embed()

    assert seen == [None]


@pytest.mark.parametrize("pager_fails", [False, True])
def test_pager_receives_exact_text_and_always_removes_its_file(
    monkeypatch, pager_fails
):
    import shlex

    import IPython

    from scitex_repl import less

    paths = []

    def system(command):
        argv = shlex.split(command)
        assert argv[0] == "less"
        path = Path(argv[1])
        paths.append(path)
        assert path.read_text() == "first line\nsecond line\n"
        if pager_fails:
            raise RuntimeError("synthetic pager failure")

    shell = Mock(system=system)
    monkeypatch.setattr(IPython, "get_ipython", lambda: shell)

    if pager_fails:
        with pytest.raises(RuntimeError, match="synthetic pager failure"):
            less("first line\nsecond line\n")
    else:
        assert less("first line\nsecond line\n") is None

    assert len(paths) == 1
    assert not paths[0].exists()


def test_pager_without_ipython_refuses_before_creating_tempfile(monkeypatch):
    import tempfile

    import IPython

    from scitex_repl import less

    create = Mock(side_effect=AssertionError("must refuse before creating a file"))
    monkeypatch.setattr(IPython, "get_ipython", lambda: None)
    monkeypatch.setattr(tempfile, "NamedTemporaryFile", create)

    with pytest.raises(RuntimeError, match="active IPython shell"):
        less("synthetic text")

    create.assert_not_called()
