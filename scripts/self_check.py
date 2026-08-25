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
        skill_source = Path(tmp) / "systematic-debugging"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text(
            "---\nname: systematic-debugging\ndescription: Smoke test skill.\n---\n",
            encoding="utf-8",
        )
        run(str(SCRIPTS / "init_project_os.py"), "--target", str(target), "--date", "2026-08-25")
        run(
            str(SCRIPTS / "install_project_integration.py"),
            "--target",
            str(target),
            "--id",
            "superpowers",
            "--skill",
            "systematic-debugging",
            "--source-dir",
            str(skill_source),
        )
        run(
            str(SCRIPTS / "install_project_integration.py"),
            "--target",
            str(target),
            "--id",
            "context7",
            "--command",
            "npx",
            "--arg=@upstash/context7-mcp",
        )
        run(str(SCRIPTS / "validate_project_os.py"), "--target", str(target))

    print("PROJECT INTEGRATIONS CHECKED")
    print("SELF CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
