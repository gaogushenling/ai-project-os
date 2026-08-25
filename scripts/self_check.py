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

# Bilingual documentation layout: English is the default, and every
# human-facing document ships with a linked Chinese translation.
BILINGUAL_DOCS = (
    (ROOT / "README.md", ROOT / "README_zh.md"),
    (ROOT / "SKILL.md", ROOT / "SKILL_zh.md"),
    (ROOT / "docs" / "getting-started.md", ROOT / "docs" / "getting-started_zh.md"),
    (
        ROOT / "references" / "recommended-integrations.md",
        ROOT / "references" / "recommended-integrations_zh.md",
    ),
)


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def check_bilingual_docs() -> None:
    """Verify the bilingual docs: English defaults, zh translations, mutual links."""
    for default, translated in BILINGUAL_DOCS:
        if not default.is_file():
            raise ValueError(f"Missing default documentation: {default.relative_to(ROOT)}")
        if not translated.is_file():
            raise ValueError(f"Missing Chinese translation: {translated.relative_to(ROOT)}")
        default_text = default.read_text(encoding="utf-8")
        translated_text = translated.read_text(encoding="utf-8")
        if translated.name not in default_text or default.name not in translated_text:
            raise ValueError(
                f"Language links missing between {default.name} and {translated.name}"
            )
        cjk_lines = [line for line in default_text.splitlines() if has_cjk(line)]
        if len(cjk_lines) > 2:
            raise ValueError(
                f"{default.relative_to(ROOT)} must default to English; "
                f"found {len(cjk_lines)} Chinese lines"
            )


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
    check_bilingual_docs()

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

    print("BILINGUAL DOCS CHECKED")
    print("PROJECT INTEGRATIONS CHECKED")
    print("SELF CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
