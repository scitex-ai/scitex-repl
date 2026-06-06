# Changelog

All notable changes to `scitex-repl` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] — 2026-06-07

- Initial release. Hosts the interactive REPL helpers ported out of
  `scitex_gen._ipython` as part of the scitex-gen full retirement wave
  (Phase B):
  - `embed` — drop into an IPython shell with the clipboard content
    optionally pre-executed. The upstream module was largely a
    commented-out scaffold; the single working helper is preserved
    here with the same prompt behavior.
  - `less` — pipe a string into the system `less` pager from inside
    an IPython session.
  - `paste` — exec the system clipboard contents (after `textwrap.dedent`),
    swallowing exec exceptions.
- Runtime dependencies: `ipython`, `pyperclip`.
