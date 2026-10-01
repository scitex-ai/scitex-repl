# Changelog

All notable changes to `scitex-repl` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.2] — 2026-10-02

- Keep the PR #11 audit, import, and synthetic-clipboard diagnostic fixes.
- Execute confirmed clipboard content before opening the actual IPython shell;
  preserve its namespace and do not treat IPython.embed()'s None as a shell.
- Quote pager paths, refuse missing IPython before creating a file, and clean
  the temporary file when the pager raises.
- Verify the declared CPU SIF digest, resolve an optional shim or PATH
  Apptainer, and use job-owned scratch without requiring GPFS.
- Require the full declared extras and execute native end-to-end tests with
  `RUN_E2E=1`; isolate SciTeX, IPython, installer, and pytest state per job.
- Validate wheel and sdist metadata and installed-wheel imports before upload.
- Require current Logger >=0.2.2 and Dev >=0.62.1; Python >=3.10 matches
  the Logger runtime dependency.


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
