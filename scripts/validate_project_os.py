#!/usr/bin/env python3
"""Validate an initialized AI Project OS layer."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED_FILES = (
    "AGENTS.md",
    ".codex/skills/project-memory/SKILL.md",
    "docs/ai/project.json",
    "docs/ai/routes.json",
    "docs/ai/memory.json",
)

JSON_CONTRACTS = {
    "docs/ai/project.json": ("schema_version", "project", "commands", "confirm_before"),
    "docs/ai/routes.json": ("schema_version", "default", "routes"),
    "docs/ai/memory.json": ("schema_version", "tool_failures", "corrections", "regressions"),
}

GITIGNORE_RULES = (".codex/local/", ".env", ".env.*", "!.env.example", "*.local.json")

REQUIRED_ROUTE_GATES = {
    "develop": {
        "define_user_outcome",
        "define_minimum_complete_scope",
        "check_relevant_product_risks",
        "define_acceptance_evidence",
    },
    "verify": {"engineering_verification", "user_flow_acceptance"},
}

SECRET_PATTERNS = (
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|token|password|secret|private[_-]?key|connection[_-]?string)\b"
        r"\s*[:=]\s*[\"']?[^\s\"']{8,}"
    ),
)


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


def load_json(path: Path, relative: str, findings: list[Finding]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        findings.append(Finding("ERROR", "json-invalid", str(error), relative))
        return None


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

    gitignore = root / ".gitignore"
    gitignore_text = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
    for rule in GITIGNORE_RULES:
        if rule not in gitignore_text.splitlines():
            findings.append(Finding("ERROR", "gitignore-rule-missing", f"Missing local-only ignore rule: {rule}", ".gitignore"))

    scan_files = [root / relative for relative in REQUIRED_FILES if (root / relative).is_file()] + logs
    for path in scan_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(Finding("ERROR", "possible-secret", "Possible secret in committed project memory", path.relative_to(root).as_posix()))

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
