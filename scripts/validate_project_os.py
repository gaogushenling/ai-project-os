#!/usr/bin/env python3
"""Validate an initialized AI Project OS layer."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))
from _common import SECRET_PATTERNS, tree_hash  # noqa: E402


REQUIRED_FILES = (
    "AGENTS.md",
    ".agents/skills/project-memory/SKILL.md",
    "docs/ai/capabilities.json",
    "docs/ai/capabilities.lock.json",
    "docs/ai/project.json",
    "docs/ai/routes.json",
    "docs/ai/memory.json",
)

JSON_CONTRACTS = {
    "docs/ai/capabilities.json": (
        "schema_version",
        "default_scope",
        "skill_directory",
        "mcp_config",
        "install_all",
        "capabilities",
    ),
    "docs/ai/capabilities.lock.json": ("schema_version", "scope", "capabilities"),
    "docs/ai/project.json": ("schema_version", "project", "commands", "confirm_before"),
    "docs/ai/routes.json": ("schema_version", "default", "routes"),
    "docs/ai/memory.json": ("schema_version", "entry_contract", "tool_failures", "corrections", "regressions"),
}

GITIGNORE_RULES = (
    ".codex/local/",
    ".agents/local/",
    ".env",
    ".env.*",
    "!.env.example",
    "*.local.json",
)

REQUIRED_ROUTE_GATES = {
    "develop": {
        "define_user_outcome",
        "define_minimum_complete_scope",
        "check_relevant_product_risks",
        "define_acceptance_evidence",
    },
    "verify": {"engineering_verification", "user_flow_acceptance"},
}


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str
    path: str | None = None


def contains_placeholder(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().upper().startswith("TODO")
    if isinstance(value, list):
        return any(contains_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(contains_placeholder(item) for item in value.values())
    return False


def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def safe_declared_path(root: Path, declared: object) -> bool:
    if not isinstance(declared, str) or not declared:
        return False
    relative = Path(declared)
    if relative.is_absolute():
        return False
    return inside(root, (root / relative).resolve())


def mcp_managed_block(text: str, integration_id: str) -> str | None:
    """Return the installer-managed TOML block for an MCP id, or None."""
    begin = f"# BEGIN AI PROJECT OS MCP {integration_id}"
    end = f"# END AI PROJECT OS MCP {integration_id}"
    start = text.find(begin)
    if start == -1:
        return None
    finish = text.find(end, start + len(begin))
    if finish == -1:
        return None
    return text[start : finish + len(end) + 1]


def load_json(path: Path, relative: str, findings: list[Finding]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        findings.append(Finding("ERROR", "json-invalid", str(error), relative))
        return None


def read_text_or_report(path: Path, relative: str, findings: list[Finding]) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        findings.append(Finding("ERROR", "file-unreadable", f"Cannot read file: {error}", relative))
        return None


def validate_memory_entries(memory: dict, findings: list[Finding]) -> None:
    contract = memory.get("entry_contract")
    if not isinstance(contract, dict):
        findings.append(
            Finding("ERROR", "json-contract", "entry_contract must be an object", "docs/ai/memory.json")
        )
        return
    required_fields = contract.get("required")
    if not isinstance(required_fields, list):
        findings.append(
            Finding("ERROR", "json-contract", "entry_contract.required must be a list", "docs/ai/memory.json")
        )
        return
    required = set(required_fields)
    for section in ("tool_failures", "corrections", "regressions"):
        entries = memory.get(section)
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries, start=1):
            location = f"{section}[{index}]"
            if not isinstance(entry, dict):
                findings.append(
                    Finding("ERROR", "memory-entry-contract", f"{location} must be an object", "docs/ai/memory.json")
                )
                continue
            missing = sorted(key for key in required if not entry.get(key))
            if missing:
                findings.append(
                    Finding(
                        "ERROR",
                        "memory-entry-contract",
                        f"{location} is missing verified fields: {', '.join(missing)}",
                        "docs/ai/memory.json",
                    )
                )
            expires_at = entry.get("expires_at")
            if isinstance(expires_at, str):
                try:
                    expired = dt.date.fromisoformat(expires_at) < dt.date.today()
                except ValueError:
                    findings.append(
                        Finding("ERROR", "memory-entry-contract", f"{location} has an invalid expires_at date", "docs/ai/memory.json")
                    )
                else:
                    if expired:
                        findings.append(
                            Finding("WARNING", "memory-entry-expired", f"{location} has passed expires_at; re-verify or remove it", "docs/ai/memory.json")
                        )


def validate_route_targets(
    root: Path,
    name: str,
    route: object,
    findings: list[Finding],
) -> None:
    if not isinstance(route, dict) or not isinstance(route.get("read"), list):
        findings.append(Finding("ERROR", "json-contract", f"Route {name!r} must define a read list", "docs/ai/routes.json"))
        return
    for relative in route["read"]:
        if not isinstance(relative, str):
            findings.append(Finding("ERROR", "json-contract", f"Route {name!r} has a non-string target", "docs/ai/routes.json"))
            continue
        candidate = (root / relative).resolve()
        if not inside(root, candidate):
            findings.append(Finding("ERROR", "route-target-unsafe", f"Route {name!r} reads outside the project", relative))
        elif not candidate.is_file():
            findings.append(Finding("ERROR", "route-target-missing", f"Route {name!r} target does not exist", relative))


def validate(target: Path) -> list[Finding]:
    root = target.resolve()
    findings: list[Finding] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            findings.append(Finding("ERROR", "required-file-missing", "Required file is missing", relative))

    logs = list((root / "docs/ai/logs").glob("*.md")) if (root / "docs/ai/logs").is_dir() else []
    if not logs:
        findings.append(Finding("ERROR", "required-file-missing", "At least one operation log is required", "docs/ai/logs/"))

    parsed: dict[str, object] = {}
    for relative, required_keys in JSON_CONTRACTS.items():
        path = root / relative
        if not path.is_file():
            continue
        data = load_json(path, relative, findings)
        if data is None:
            continue
        parsed[relative] = data
        if not isinstance(data, dict):
            findings.append(Finding("ERROR", "json-contract", "Top-level value must be an object", relative))
            continue
        for key in required_keys:
            if key not in data:
                findings.append(Finding("ERROR", "json-contract", f"Missing key: {key}", relative))
        if data.get("schema_version") != 1:
            findings.append(Finding("ERROR", "schema-version", "Expected schema_version 1", relative))

    project = parsed.get("docs/ai/project.json")
    if isinstance(project, dict) and contains_placeholder(project):
        findings.append(Finding("WARNING", "project-placeholder", "Project facts still contain TODO placeholders", "docs/ai/project.json"))

    memory = parsed.get("docs/ai/memory.json")
    if isinstance(memory, dict):
        validate_memory_entries(memory, findings)

    routes = parsed.get("docs/ai/routes.json")
    if isinstance(routes, dict):
        validate_route_targets(root, "default", routes.get("default"), findings)
        route_items = routes.get("routes", {})
        if not isinstance(route_items, dict) or not route_items:
            findings.append(Finding("ERROR", "json-contract", "At least one route is required", "docs/ai/routes.json"))
        else:
            for name, route in route_items.items():
                validate_route_targets(root, str(name), route, findings)
            for name, required_gates in REQUIRED_ROUTE_GATES.items():
                route = route_items.get(name, {})
                actual_gates = route.get("gates", []) if isinstance(route, dict) else []
                missing_gates = required_gates - set(actual_gates if isinstance(actual_gates, list) else [])
                if missing_gates:
                    findings.append(
                        Finding(
                            "ERROR",
                            "route-gates-missing",
                            f"Route {name!r} is missing gates: {', '.join(sorted(missing_gates))}",
                            "docs/ai/routes.json",
                        )
                    )

    capabilities = parsed.get("docs/ai/capabilities.json")
    capability_lock = parsed.get("docs/ai/capabilities.lock.json")
    manifest_ids: set[str] = set()
    lock_ids: set[str] = set()
    if isinstance(capabilities, dict):
        if capabilities.get("default_scope") != "project":
            findings.append(
                Finding(
                    "ERROR",
                    "capability-scope-invalid",
                    "Capabilities must default to project scope",
                    "docs/ai/capabilities.json",
                )
            )
        for field in ("skill_directory", "mcp_config"):
            if not safe_declared_path(root, capabilities.get(field)):
                findings.append(
                    Finding(
                        "ERROR",
                        "capability-path-invalid",
                        f"{field} must be a non-empty path inside the project",
                        "docs/ai/capabilities.json",
                    )
                )
        if capabilities.get("install_all") is not False:
            findings.append(
                Finding(
                    "ERROR",
                    "capability-install-all",
                    "Projects must select the minimum required capabilities",
                    "docs/ai/capabilities.json",
                )
            )
        items = capabilities.get("capabilities")
        if not isinstance(items, list):
            findings.append(
                Finding("ERROR", "json-contract", "capabilities must be a list", "docs/ai/capabilities.json")
            )
        else:
            for item in items:
                if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                    findings.append(
                        Finding("ERROR", "json-contract", "Capability entries require an id", "docs/ai/capabilities.json")
                    )
                    continue
                capability_id = item["id"]
                manifest_ids.add(capability_id)
                if item.get("scope") != "project":
                    findings.append(
                        Finding(
                            "ERROR",
                            "capability-scope-invalid",
                            f"Capability {capability_id!r} is not project scoped",
                            "docs/ai/capabilities.json",
                        )
                    )
                state = item.get("state")
                state_keys = {"installed", "enabled", "configured", "verified"}
                if not isinstance(state, dict) or any(
                    not isinstance(state.get(key), bool) for key in state_keys
                ):
                    findings.append(
                        Finding(
                            "ERROR",
                            "capability-state-invalid",
                            f"Capability {capability_id!r} requires boolean lifecycle state",
                            "docs/ai/capabilities.json",
                        )
                    )
                    continue
                if item.get("type") == "skill-project" and state["installed"]:
                    selected = item.get("selected_skills", [])
                    if not isinstance(selected, list) or not selected:
                        findings.append(
                            Finding("ERROR", "capability-install-invalid", "Installed skill project has no selected skills", "docs/ai/capabilities.json")
                        )
                    else:
                        for skill in selected:
                            relative = skill.get("installed_path") if isinstance(skill, dict) else None
                            if not isinstance(relative, str):
                                findings.append(
                                    Finding("ERROR", "capability-install-invalid", "Installed skill has no project path", "docs/ai/capabilities.json")
                                )
                                continue
                            candidate = (root / relative).resolve()
                            if not inside(root, candidate):
                                findings.append(
                                    Finding("ERROR", "capability-path-invalid", "Installed skill path escapes the project", relative)
                                )
                            elif not (candidate / "SKILL.md").is_file():
                                findings.append(
                                    Finding("ERROR", "capability-install-missing", "Installed skill is missing SKILL.md", relative)
                                )
                if item.get("type") == "mcp-server" and state["configured"]:
                    mcp_config = capabilities.get("mcp_config")
                    if safe_declared_path(root, mcp_config) and not (root / mcp_config).is_file():
                        findings.append(
                            Finding(
                                "ERROR",
                                "capability-config-missing",
                                "Configured MCP server has no project config",
                                mcp_config,
                            )
                        )

    if isinstance(capability_lock, dict):
        if capability_lock.get("scope") != "project":
            findings.append(
                Finding("ERROR", "capability-scope-invalid", "Capability lock must be project scoped", "docs/ai/capabilities.lock.json")
            )
        locked_items = capability_lock.get("capabilities")
        if isinstance(locked_items, list):
            lock_ids = {
                item["id"]
                for item in locked_items
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            for item in locked_items:
                if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                    continue
                locked_id = item["id"]
                if item.get("type") == "skill-project":
                    selected = item.get("selected_skills", [])
                    if not isinstance(selected, list):
                        continue
                    for skill in selected:
                        if not isinstance(skill, dict) or not isinstance(skill.get("installed_path"), str):
                            continue
                        skill_relative = skill["installed_path"]
                        skill_root = (root / skill_relative).resolve()
                        if not inside(root, skill_root) or not skill_root.is_dir():
                            continue
                        expected = skill.get("content_sha256")
                        if not isinstance(expected, str) or not expected:
                            findings.append(
                                Finding(
                                    "WARNING",
                                    "capability-hash-missing",
                                    f"Locked skill has no content hash: {skill_relative}",
                                    "docs/ai/capabilities.lock.json",
                                )
                            )
                            continue
                        if tree_hash(skill_root) != expected:
                            findings.append(
                                Finding(
                                    "ERROR",
                                    "capability-hash-mismatch",
                                    f"Installed skill content drifted from the lock: {skill_relative}",
                                    "docs/ai/capabilities.lock.json",
                                )
                            )
                elif item.get("type") == "mcp-server":
                    config_relative = item.get("config_path")
                    if not isinstance(config_relative, str):
                        continue
                    config_resolved = (root / config_relative).resolve()
                    if not inside(root, config_resolved):
                        continue
                    expected = item.get("config_sha256")
                    if not isinstance(expected, str) or not expected:
                        findings.append(
                            Finding(
                                "WARNING",
                                "capability-hash-missing",
                                f"Locked MCP config has no config hash: {config_relative}",
                                "docs/ai/capabilities.lock.json",
                            )
                        )
                        continue
                    if not config_resolved.is_file():
                        continue
                    config_text = read_text_or_report(config_resolved, config_relative, findings)
                    if config_text is None:
                        continue
                    block = mcp_managed_block(config_text, locked_id)
                    if block is None:
                        findings.append(
                            Finding(
                                "ERROR",
                                "capability-config-drift",
                                f"MCP config is missing the locked managed block: {locked_id}",
                                "docs/ai/capabilities.lock.json",
                            )
                        )
                    elif hashlib.sha256(block.encode("utf-8")).hexdigest() != expected:
                        findings.append(
                            Finding(
                                "ERROR",
                                "capability-hash-mismatch",
                                f"MCP managed config drifted from the lock: {locked_id}",
                                "docs/ai/capabilities.lock.json",
                            )
                        )
    if manifest_ids != lock_ids:
        findings.append(
            Finding(
                "ERROR",
                "capability-lock-drift",
                "Capability manifest and lock contain different integration ids",
                "docs/ai/capabilities.lock.json",
            )
        )

    gitignore = root / ".gitignore"
    gitignore_text = (
        read_text_or_report(gitignore, ".gitignore", findings) if gitignore.is_file() else ""
    )
    if gitignore_text is not None:
        for rule in GITIGNORE_RULES:
            if rule not in gitignore_text.splitlines():
                findings.append(
                    Finding("ERROR", "gitignore-rule-missing", f"Missing local-only ignore rule: {rule}", ".gitignore")
                )

    scan_files = [root / relative for relative in REQUIRED_FILES if (root / relative).is_file()] + logs
    for path in scan_files:
        relative = path.relative_to(root).as_posix()
        text = read_text_or_report(path, relative, findings)
        if text is None:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(Finding("ERROR", "possible-secret", "Possible secret in committed project memory", relative))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Target repository root")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args()

    target = Path(args.target)
    findings = validate(target)
    errors = sum(item.level == "ERROR" for item in findings)
    warnings = sum(item.level == "WARNING" for item in findings)
    status = "fail" if errors else "pass"
    payload = {
        "status": status,
        "target": str(target.resolve()),
        "summary": {"errors": errors, "warnings": warnings},
        "findings": [asdict(item) for item in findings],
    }

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"AI Project OS validation: status={status} errors={errors} warnings={warnings}")
        for item in findings:
            location = f" [{item.path}]" if item.path else ""
            print(f"{item.level} {item.code}{location}: {item.message}")

    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
