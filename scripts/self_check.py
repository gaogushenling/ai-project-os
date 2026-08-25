#!/usr/bin/env python3
"""Run a dependency-free smoke check of the complete skill package."""

from __future__ import annotations

import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(*args: str) -> None:
    subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def main() -> int:
    for script in sorted(SCRIPTS.glob("*.py")):
        py_compile.compile(str(script), doraise=True)

    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "smoke-project"
        run(str(SCRIPTS / "init_project_os.py"), "--target", str(target), "--date", "2026-08-25")
        run(str(SCRIPTS / "validate_project_os.py"), "--target", str(target))

    print("SELF CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
