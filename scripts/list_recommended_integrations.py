#!/usr/bin/env python3
"""List verified public-source Skill projects and MCP recommendations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "references" / "recommended-integrations.json"
TIER_ORDER = ["baseline", "scenario", "production-risk"]


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def select_items(
    catalog: dict[str, Any],
    *,
    integration_type: str | None,
    tier: str | None,
    tag: str | None,
    license_kind: str | None,
) -> list[dict[str, Any]]:
    items = [*catalog["skill_projects"], *catalog["mcp_servers"]]
    if integration_type:
        items = [item for item in items if item["type"] == integration_type]
    if tier:
        items = [
            item
            for item in items
            if item["tier"] == tier
            or any(
                skill["tier"] == tier for skill in item.get("recommended_skills", [])
            )
        ]
    if tag:
        normalized_tag = tag.lower()
        items = [
            item
            for item in items
            if normalized_tag in item["tags"]
            or any(
                normalized_tag in skill["tags"]
                for skill in item.get("recommended_skills", [])
            )
        ]
    if license_kind:
        items = [item for item in items if item["license_kind"] == license_kind]
    return items


def render_text(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No verified recommendations match the filters.\n"

    lines = ["Verified recommendations (review source before installation):"]
    for item in items:
        tiers = {item["tier"]}
        tiers.update(
            skill["tier"] for skill in item.get("recommended_skills", [])
        )
        tier_label = ", ".join(tier for tier in TIER_ORDER if tier in tiers)
        lines.extend([
            f"- {item['name']} [{item['type']} / {tier_label}]",
            f"  Repository: {item['repository_url']}",
            f"  License: {item['license_id']} [{item['license_kind']}] ({item['license_url']})",
        ])
        if item["type"] == "skill-project":
            names = ", ".join(
                skill["name"] for skill in item["recommended_skills"]
            )
            lines.append(f"  Highlighted skills: {names}")
    lines.append("Nothing was installed or enabled.")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List verified public-source Skill projects and MCP recommendations."
    )
    parser.add_argument("--type", choices=["skill-project", "mcp-server"])
    parser.add_argument(
        "--tier", choices=["baseline", "scenario", "production-risk"]
    )
    parser.add_argument("--tag", help="Match one exact catalog tag.")
    parser.add_argument(
        "--license-kind", choices=["open-source", "source-available"]
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    catalog = load_catalog()
    items = select_items(
        catalog,
        integration_type=args.type,
        tier=args.tier,
        tag=args.tag,
        license_kind=args.license_kind,
    )

    if args.format == "json":
        print(
            json.dumps(
                {
                    "policy": catalog["policy"],
                    "count": len(items),
                    "items": items,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(render_text(items), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
