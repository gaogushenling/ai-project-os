---
name: ai-project-os
description: Initialize and operate a lightweight project-level AI collaboration layer with progressive context loading, project facts, task routing, failure memory, and delivery validation.
---

# AI Project OS

Use this skill to give a repository a small, durable collaboration layer for AI coding agents. Keep the skill generic; keep project-specific facts inside the project.

## Enter a project

1. Read the project `AGENTS.md`.
2. Read `.codex/skills/project-memory/SKILL.md` when present.
3. Match the request against `docs/ai/routes.json`.
4. Load only the files named by the matched route.
5. Treat current user instructions, code, tests, and project-native rules as more authoritative than recorded memory.

Do not load every project-memory file by default. Progressive loading is the main context-control mechanism.

## Initialize

Preview before writing to an existing project:

```powershell
python scripts/init_project_os.py --target <project-root> --dry-run
```

Apply without overwriting existing files:

```powershell
python scripts/init_project_os.py --target <project-root>
```

Use `--force` only when replacing the generated layer is intentional.

## Project memory contract

- `docs/ai/project.json`: stable project facts, source-of-truth pointers, commands, quality gates, and risk boundaries.
- `docs/ai/routes.json`: request signals and the minimum project context to load.
- `docs/ai/memory.json`: verified tool failures, user corrections, and regression-prevention records.
- `docs/ai/logs/`: concise evidence from meaningful operations and verification.

Write facts to the narrowest matching file. Do not copy methodology manuals, chat transcripts, secrets, or speculative notes into project memory.

## Product work protocol

For non-trivial product changes:

- Start from the user-visible outcome and real constraints. Choose the simplest mechanism that closes the required loop; do not start from available technology or a generic checklist.
- Define the user, current flow, target flow, smallest complete scope, important failure paths, and acceptance evidence before implementation.
- Check UI, API, backend, data, transactions, idempotency, concurrency, indexes, performance, permissions, audit, and observability only when relevant to the outcome or a material risk.
- Classify adjacent issues as a current blocker, a required risk to handle now, or a later improvement. Implement only the first two.
- Communicate the conclusion first in plain language. Add technical depth only when it helps the reader decide, implement, or verify.

## Operate

- Before running project commands, use the command recorded in `docs/ai/project.json` and check relevant failures in `docs/ai/memory.json`.
- After a tool failure, correction, or recurring defect, record evidence only when it will change future behavior.
- Ask before production changes, destructive data operations, credential handling, or other actions marked for confirmation by project facts.
- At delivery, distinguish implementation, engineering verification, and product acceptance. Report what remains unverified.

## Validate

```powershell
python scripts/validate_project_os.py --target <project-root>
python scripts/validate_project_os.py --target <project-root> --strict
python scripts/self_check.py
```

Validation checks required files, JSON structure, route safety, local-only ignore rules, unresolved placeholders, and likely secrets.
