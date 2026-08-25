#!/usr/bin/env python3
"""Initialize the minimal AI Project OS layer in a repository.

Template and protocol files can be refreshed with --force. Project data
files under docs/ai (facts, memory, capability manifest and lock) are
never overwritten once they exist; resetting them requires deleting them
first.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "project-os"
GITIGNORE_ASSET = ASSET_ROOT / ".gitignore.append"

# Project-owned data files: never overwritten by the initializer, even
# with --force. They accumulate user-filled facts and install state.
STATE_FILES = {
    Path("docs/ai/project.json"),
    Path("docs/ai/memory.json"),
    Path("docs/ai/capabilities.json"),
    Path("docs/ai/capabilities.lock.json"),
}

sys.path.insert(0, str(ROOT / "scripts"))
from _common import SECRET_PATTERNS  # noqa: E402


def assert_safe_asset(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        raise ValueError(f"Refusing sensitive template asset: {path}")


def render_path(relative: Path, date: str) -> Path:
    return Path(*(part.replace("{{date}}", date) for part in relative.parts))


def render_text(text: str, *, date: str, project_name: str) -> str:
    escaped_name = json.dumps(project_name, ensure_ascii=False)[1:-1]
    return text.replace("{{date}}", date).replace("{{project_name}}", escaped_name)


def normalize_date(value: str) -> str:
    try:
        normalized = dt.date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise ValueError("date must use YYYY-MM-DD") from error
    if value != normalized:
        raise ValueError("date must use YYYY-MM-DD")
    return normalized


def date_argument(value: str) -> str:
    try:
        return normalize_date(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def asset_files() -> list[Path]:
    files = [path for path in ASSET_ROOT.rglob("*") if path.is_file() and path != GITIGNORE_ASSET]
    for path in files:
        assert_safe_asset(path)
    return sorted(files)


def update_gitignore(target: Path, *, dry_run: bool) -> str:
    assert_safe_asset(GITIGNORE_ASSET)
    block = GITIGNORE_ASSET.read_text(encoding="utf-8").strip() + "\n"
    path = target / ".gitignore"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if block.strip() in existing:
        return "skipped"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        separator = "" if not existing or existing.endswith("\n") else "\n"
        path.write_text(existing + separator + block, encoding="utf-8", newline="\n")
    return "appended"


def initialize(
    target: Path,
    *,
    date: str,
    force: bool = False,
    dry_run: bool = False,
) -> list[tuple[str, str]]:
    date = normalize_date(date)
    resolved = target.resolve()
    results: list[tuple[str, str]] = []
    for source in asset_files():
        relative = render_path(source.relative_to(ASSET_ROOT), date)
        destination = resolved / relative
        exists = destination.exists()
        if exists and relative in STATE_FILES:
            action = "protected"
        elif exists and not force:
            action = "skipped"
        else:
            action = "overwritten" if exists else "created"
            if not dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)
                rendered = render_text(
                    source.read_text(encoding="utf-8"),
                    date=date,
                    project_name=resolved.name,
                )
                destination.write_text(rendered, encoding="utf-8", newline="\n")
        results.append((action, relative.as_posix()))

    results.append((update_gitignore(resolved, dry_run=dry_run), ".gitignore"))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Target repository root")
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        type=date_argument,
        help="Date for the initial log (YYYY-MM-DD)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite generated files")
    args = parser.parse_args()

    target = Path(args.target)
    results = initialize(target, date=args.date, force=args.force, dry_run=args.dry_run)
    mode = "DRY RUN" if args.dry_run else "INITIALIZED"
    print(f"AI Project OS {mode}: {target.resolve()}")
    for action, relative in results:
        print(f"{action:11} {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
