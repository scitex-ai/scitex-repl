"""Validate REPL's wheel/sdist identity before either can be published."""

from __future__ import annotations

import email
import hashlib
import json
import os
import sys
import tarfile
import zipfile
from pathlib import Path

import tomllib


def validate(directory: Path) -> dict:
    project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
    version = project["version"]
    tag = os.environ.get("SCITEX_REPL_RELEASE_TAG")
    if tag and tag != f"v{version}":
        raise ValueError(
            f"release tag {tag!r} does not match source version {version!r}"
        )
    wheels = list(directory.glob("*.whl"))
    sdists = list(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1 or len(list(directory.iterdir())) != 2:
        raise ValueError("dist must contain exactly one wheel and one sdist")
    with zipfile.ZipFile(wheels[0]) as wheel:
        metadata_names = [
            name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_names) != 1:
            raise ValueError("wheel must contain one distribution metadata record")
        wheel_metadata = email.message_from_bytes(wheel.read(metadata_names[0]))
        required = {
            f"scitex_repl/{name}.py"
            for name in ("__init__", "_embed", "_less", "_paste")
        }
        if not required <= set(wheel.namelist()):
            raise ValueError("wheel is missing a public implementation module")
    with tarfile.open(sdists[0]) as sdist:
        names = sdist.getnames()
        metadata_names = [
            name
            for name in names
            if name.count("/") == 1 and name.endswith("/PKG-INFO")
        ]
        if len(metadata_names) != 1:
            raise ValueError("sdist must contain one top-level metadata record")
        sdist_metadata = email.message_from_bytes(
            sdist.extractfile(metadata_names[0]).read()
        )
        prefix = metadata_names[0].split("/", 1)[0]
        required = {
            "pyproject.toml",
            "README.md",
            "CHANGELOG.md",
            "LICENSE",
            "examples/quickstart.py",
            "tests/conftest.py",
            "tests/e2e/conftest.py",
            "tests/e2e/test_paste_diagnostic_workflow.py",
        }
        if not {f"{prefix}/{name}" for name in required} <= set(names):
            raise ValueError("sdist is missing native test/example or release inputs")
    for metadata in (wheel_metadata, sdist_metadata):
        if metadata["Name"] != "scitex-repl" or metadata["Version"] != version:
            raise ValueError("artifact identity does not match the REPL source")
        if set(metadata.get_all("Provides-Extra", [])) != {"all", "dev", "docs"}:
            raise ValueError("artifact omitted a declared REPL extra")
    return {
        "name": "scitex-repl",
        "version": version,
        "release_tag": tag,
        "artifacts": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (wheels[0], sdists[0])
        },
    }


if __name__ == "__main__":
    print(json.dumps(validate(Path(sys.argv[1])), indent=2))
