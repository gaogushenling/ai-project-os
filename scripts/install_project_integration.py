#!/usr/bin/env python3
"""Install or configure one catalog integration at project scope."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "references" / "recommended-integrations.json"
MANIFEST_PATH = Path("docs/ai/capabilities.json")
LOCK_PATH = Path("docs/ai/capabilities.lock.json")
ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")

sys.path.insert(0, str(ROOT / "scripts"))
from _common import CLI_SECRET_PATTERNS, tree_hash  # noqa: E402


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return data


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def find_integration(catalog: dict, integration_id: str) -> dict:
    items = catalog.get("skill_projects", []) + catalog.get("mcp_servers", [])
    for item in items:
        if isinstance(item, dict) and item.get("id") == integration_id:
            return item
    raise ValueError(f"Unknown integration id: {integration_id}")


def find_skill(project: dict, skill_id: str) -> dict:
    for skill in project.get("recommended_skills", []):
        if isinstance(skill, dict) and skill.get("id") == skill_id:
            return skill
    raise ValueError(f"Skill {skill_id!r} is not listed under {project.get('id')!r}")


def ensure_project(target: Path) -> tuple[Path, dict, dict]:
    root = target.resolve()
    manifest_file = root / MANIFEST_PATH
    lock_file = root / LOCK_PATH
    if not manifest_file.is_file() or not lock_file.is_file():
        raise ValueError("Target is not initialized; run init_project_os.py first")
    manifest = read_json(manifest_file)
    lock = read_json(lock_file)
    if manifest.get("default_scope") != "project" or lock.get("scope") != "project":
        raise ValueError("Target capability files are not project scoped")
    project_relative_path(root, manifest.get("skill_directory"), "skill_directory")
    project_relative_path(root, manifest.get("mcp_config"), "mcp_config")
    return root, manifest, lock


def project_relative_path(root: Path, declared: object, field: str) -> Path:
    if not isinstance(declared, str) or not declared:
        raise ValueError(f"{field} in capabilities.json must be a non-empty project-relative path")
    relative = Path(declared)
    if relative.is_absolute() or not (root / relative).resolve().is_relative_to(root):
        raise ValueError(f"{field} must stay inside the project")
    return relative


def validate_env_names(names: list[str]) -> None:
    for name in names:
        if not ENV_NAME.fullmatch(name):
            raise ValueError(f"Environment variable must be a name, not a value: {name!r}")


def reject_direct_secrets(values: list[str]) -> None:
    for value in values:
        if any(pattern.search(value) for pattern in CLI_SECRET_PATTERNS):
            raise ValueError("Credential values are not allowed in project configuration; use an environment variable name")


def merge_by_id(items: list[dict], item: dict) -> list[dict]:
    merged = [existing for existing in items if existing.get("id") != item["id"]]
    merged.append(item)
    return sorted(merged, key=lambda value: value["id"])


def base_manifest_entry(integration: dict) -> dict:
    return {
        "id": integration["id"],
        "name": integration["name"],
        "type": integration["type"],
        "scope": "project",
        "source_url": integration["source_url"],
        "license_id": integration["license_id"],
        "license_kind": integration["license_kind"],
    }


def base_lock_entry(integration: dict) -> dict:
    return {
        "id": integration["id"],
        "type": integration["type"],
        "scope": "project",
        "source_url": integration["source_url"],
        "license_id": integration["license_id"],
        "license_kind": integration["license_kind"],
    }


def github_skill_location(project: dict, skill: dict) -> tuple[str, str]:
    source_url = skill["source_url"]
    repository_url = project["repository_url"].rstrip("/")
    prefix = repository_url + "/tree/"
    if not source_url.startswith(prefix):
        raise ValueError("Skill source URL does not identify a repository tree path")
    remainder = source_url[len(prefix) :]
    reference, separator, relative = remainder.partition("/")
    if not separator or not reference or not relative:
        raise ValueError("Skill source URL must include a revision and directory")
    return reference, relative


@contextmanager
def resolved_skill_source(
    project: dict,
    skill: dict,
    source_dir: Path | None,
) -> Iterator[tuple[Path, str]]:
    if source_dir is not None:
        resolved = source_dir.resolve()
        if not resolved.is_dir():
            raise ValueError(f"Skill source directory does not exist: {resolved}")
        yield resolved, "local"
        return

    reference, relative = github_skill_location(project, skill)
    with tempfile.TemporaryDirectory() as tmp:
        checkout = Path(tmp) / "repository"
        clone = subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                "--depth",
                "1",
                "--branch",
                reference,
                project["repository_url"],
                str(checkout),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if clone.returncode:
            raise ValueError(f"Could not clone integration source: {clone.stderr.strip()}")
        revision = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout.strip()
        resolved = checkout / Path(relative)
        if not resolved.is_dir():
            raise ValueError(f"Selected skill path is missing in the cloned revision: {relative}")
        yield resolved, revision


def combined_skill_hash(root: Path, selected: list[dict]) -> str:
    digest = hashlib.sha256()
    for item in sorted(selected, key=lambda value: value["id"]):
        path = root / item["installed_path"]
        content_hash = tree_hash(path)
        item["content_sha256"] = content_hash
        digest.update(item["id"].encode("utf-8"))
        digest.update(content_hash.encode("ascii"))
    return digest.hexdigest()


def install_skill(
    root: Path,
    manifest: dict,
    lock: dict,
    project: dict,
    skill: dict,
    *,
    source_dir: Path | None,
    force: bool,
) -> None:
    skill_directory = project_relative_path(root, manifest["skill_directory"], "skill_directory")
    destination = root / skill_directory / skill["id"]
    if destination.exists() and not force:
        raise ValueError(f"Skill already exists; use --force to replace it: {destination}")

    with resolved_skill_source(project, skill, source_dir) as (source, revision):
        if not (source / "SKILL.md").is_file():
            raise ValueError("Selected skill source does not contain SKILL.md")
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)

    existing_manifest = next(
        (item for item in manifest["capabilities"] if item.get("id") == project["id"]),
        None,
    )
    selected_manifest = list(existing_manifest.get("selected_skills", [])) if existing_manifest else []
    selected_manifest = merge_by_id(
        selected_manifest,
        {
            "id": skill["id"],
            "name": skill["name"],
            "installed_path": (skill_directory / skill["id"]).as_posix(),
        },
    )
    manifest_entry = base_manifest_entry(project)
    manifest_entry.update(
        {
            "selected_skills": selected_manifest,
            "state": {
                "installed": True,
                "enabled": True,
                "configured": True,
                "verified": False,
            },
        }
    )
    manifest["capabilities"] = merge_by_id(manifest["capabilities"], manifest_entry)

    existing_lock = next(
        (item for item in lock["capabilities"] if item.get("id") == project["id"]),
        None,
    )
    selected_lock = list(existing_lock.get("selected_skills", [])) if existing_lock else []
    selected_lock = merge_by_id(
        selected_lock,
        {
            "id": skill["id"],
            "installed_path": (skill_directory / skill["id"]).as_posix(),
        },
    )
    lock_entry = base_lock_entry(project)
    lock_entry.update(
        {
            "revision": revision,
            "selected_skills": selected_lock,
            "content_sha256": combined_skill_hash(root, selected_lock),
        }
    )
    lock["capabilities"] = merge_by_id(lock["capabilities"], lock_entry)


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_array(values: list[str]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def mcp_block(
    integration_id: str,
    *,
    command: str | None,
    args: list[str],
    env_vars: list[str],
    url: str | None,
    bearer_token_env_var: str | None,
    enabled: bool,
) -> str:
    lines = [
        f"# BEGIN AI PROJECT OS MCP {integration_id}",
        f"[mcp_servers.{integration_id}]",
    ]
    if command:
        lines.append(f"command = {toml_string(command)}")
        if args:
            lines.append(f"args = {toml_array(args)}")
        if env_vars:
            lines.append(f"env_vars = {toml_array(env_vars)}")
    if url:
        lines.append(f"url = {toml_string(url)}")
        if bearer_token_env_var:
            lines.append(f"bearer_token_env_var = {toml_string(bearer_token_env_var)}")
    lines.extend(
        [
            f"enabled = {'true' if enabled else 'false'}",
            'default_tools_approval_mode = "prompt"',
            f"# END AI PROJECT OS MCP {integration_id}",
        ]
    )
    return "\n".join(lines) + "\n"


def replace_managed_block(text: str, integration_id: str, block: str, *, force: bool) -> str:
    begin = f"# BEGIN AI PROJECT OS MCP {integration_id}"
    end = f"# END AI PROJECT OS MCP {integration_id}"
    if begin not in text and end not in text:
        unmanaged_table = re.compile(
            rf"(?m)^\s*\[mcp_servers\.(?:{re.escape(integration_id)}|\"{re.escape(integration_id)}\")\]\s*$"
        )
        if unmanaged_table.search(text):
            raise ValueError(f"MCP server already has user-managed project configuration: {integration_id}")
        separator = "" if not text or text.endswith("\n") else "\n"
        return text + separator + block
    if begin not in text or end not in text:
        raise ValueError(f"MCP config contains an incomplete managed block: {integration_id}")
    if not force:
        raise ValueError(f"MCP config already exists; use --force to replace it: {integration_id}")
    start = text.index(begin)
    finish = text.index(end, start) + len(end)
    if finish < len(text) and text[finish] == "\n":
        finish += 1
    return text[:start] + block + text[finish:]


def configure_mcp(
    root: Path,
    manifest: dict,
    lock: dict,
    integration: dict,
    *,
    command: str | None,
    args: list[str],
    env_vars: list[str],
    url: str | None,
    bearer_token_env_var: str | None,
    enabled: bool,
    force: bool,
) -> None:
    if bool(command) == bool(url):
        raise ValueError("MCP configuration requires exactly one of --command or --url")
    if args and not command:
        raise ValueError("--arg requires --command")
    if env_vars and not command:
        raise ValueError("--env-var requires --command")
    if bearer_token_env_var and not url:
        raise ValueError("--bearer-token-env-var requires --url")
    validate_env_names(env_vars)
    if bearer_token_env_var:
        validate_env_names([bearer_token_env_var])
    if url and not url.startswith("https://"):
        raise ValueError("Remote MCP URLs must use HTTPS")
    reject_direct_secrets([value for value in [command, url, *args] if value])

    block = mcp_block(
        integration["id"],
        command=command,
        args=args,
        env_vars=env_vars,
        url=url,
        bearer_token_env_var=bearer_token_env_var,
        enabled=enabled,
    )
    mcp_config = project_relative_path(root, manifest["mcp_config"], "mcp_config")
    config_path = root / mcp_config
    existing = config_path.read_text(encoding="utf-8") if config_path.is_file() else ""
    updated = replace_managed_block(existing, integration["id"], block, force=force)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(updated, encoding="utf-8", newline="\n")

    manifest_entry = base_manifest_entry(integration)
    manifest_entry.update(
        {
            "config_path": mcp_config.as_posix(),
            "state": {
                "installed": False,
                "enabled": enabled,
                "configured": True,
                "verified": False,
            },
        }
    )
    manifest["capabilities"] = merge_by_id(manifest["capabilities"], manifest_entry)

    lock_entry = base_lock_entry(integration)
    lock_entry.update(
        {
            "revision": "project-config",
            "config_path": mcp_config.as_posix(),
            "config_sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
        }
    )
    lock["capabilities"] = merge_by_id(lock["capabilities"], lock_entry)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Initialized target project")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Integration catalog")
    parser.add_argument("--id", required=True, help="Top-level integration id")
    parser.add_argument("--skill", help="Selected child skill id")
    parser.add_argument("--source-dir", type=Path, help="Use an already reviewed local skill directory")
    parser.add_argument("--command", help="Project MCP STDIO command")
    parser.add_argument("--arg", action="append", default=[], help="MCP command argument")
    parser.add_argument("--env-var", action="append", default=[], help="Environment variable name to forward")
    parser.add_argument("--url", help="Project MCP HTTPS endpoint")
    parser.add_argument("--bearer-token-env-var", help="Environment variable name holding a bearer token")
    parser.add_argument("--enable", action="store_true", help="Explicitly enable an MCP server")
    parser.add_argument(
        "--accept-license",
        help="Exact license id required for Source-Available integrations",
    )
    parser.add_argument("--force", action="store_true", help="Replace this managed project integration")
    args = parser.parse_args()

    if not SAFE_ID.fullmatch(args.id):
        parser.error("--id contains unsupported characters")
    try:
        root, manifest, lock = ensure_project(Path(args.target))
        catalog = read_json(Path(args.catalog))
        integration = find_integration(catalog, args.id)
        if (
            integration.get("license_kind") == "source-available"
            and args.accept_license != integration.get("license_id")
        ):
            raise ValueError(
                "Source-Available integration requires explicit license acceptance: "
                f"--accept-license {integration['license_id']}"
            )
        if integration["type"] == "skill-project":
            if not args.skill:
                raise ValueError("Skill projects require --skill; do not install a whole collection")
            if not SAFE_ID.fullmatch(args.skill):
                raise ValueError("--skill contains unsupported characters")
            skill = find_skill(integration, args.skill)
            install_skill(
                root,
                manifest,
                lock,
                integration,
                skill,
                source_dir=args.source_dir,
                force=args.force,
            )
            outcome = f"Installed project skill: {integration['id']}/{skill['id']}"
        else:
            if args.skill or args.source_dir:
                raise ValueError("MCP servers do not accept --skill or --source-dir")
            configure_mcp(
                root,
                manifest,
                lock,
                integration,
                command=args.command,
                args=args.arg,
                env_vars=args.env_var,
                url=args.url,
                bearer_token_env_var=args.bearer_token_env_var,
                enabled=args.enable,
                force=args.force,
            )
            state = "enabled" if args.enable else "disabled"
            outcome = f"Configured project MCP: {integration['id']} ({state})"
        write_json(root / MANIFEST_PATH, manifest)
        write_json(root / LOCK_PATH, lock)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        parser.error(str(error))

    print(outcome)
    print(f"Manifest: {(root / MANIFEST_PATH).as_posix()}")
    print(f"Lock: {(root / LOCK_PATH).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
